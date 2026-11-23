"""
Funções compartilhadas entre generate_site.py e os scripts de bin/:

- cadastro de pessoas (content/pessoas.csv)
- reuniões (gravar e e-mail de convocação)
- estagiários de uma tarefa (com a chave "ativo")
- envio de e-mail de atribuição via msmtp (conta fflchsti@usp.br)
- ajuda do Claude para redigir a descrição de uma issue
"""
import csv
import json
import os
import re
import unicodedata
from datetime import datetime
import shutil
import subprocess
import tempfile
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
PESSOAS_CSV = os.path.join(CONTENT_DIR, "pessoas.csv")

SITE_URL = "https://tiplanejamento.fflch.usp.br/"

# Conta do ~/.msmtprc usada para os avisos (from = fflchsti@usp.br)
MSMTP_ACCOUNT = "sti"
EMAIL_REMETENTE = "fflchsti@usp.br"
NOME_REMETENTE = "TI FFLCH"

# E-mails de reunião (convocação e cancelamento) saem em nome de quem organiza as reuniões.
# Enviados pela mesma conta do msmtp; para usar uma conta própria, troque MSMTP_ACCOUNT_REUNIAO
# por uma conta do ~/.msmtprc cujo "from" seja este endereço.
REMETENTE_REUNIAO = ("Thiago Gomes Veríssimo", "thiago.verissimo@usp.br")
MSMTP_ACCOUNT_REUNIAO = MSMTP_ACCOUNT

CLAUDE_MODEL = "claude-opus-5-5"


# ----------------------------------------------------------------------
# Pessoas
# ----------------------------------------------------------------------
def load_pessoas():
    """Retorna {nome: {nome, email, telefone, local, vinculo, ativo(bool)}} na ordem do CSV."""
    pessoas = {}
    if not os.path.exists(PESSOAS_CSV):
        return pessoas
    with open(PESSOAS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            nome = (row.get("nome") or "").strip()
            if not nome:
                continue
            row = {k: (v or "").strip() for k, v in row.items()}
            row["ativo"] = row.get("ativo", "sim").lower() in ("sim", "s", "true", "1", "")
            pessoas[nome] = row
    return pessoas


def pessoas_por_vinculo(vinculo, somente_ativos=True):
    return [p for p in load_pessoas().values()
            if p.get("vinculo") == vinculo and (p["ativo"] or not somente_ativos)]


def email_de(nome, pessoas=None):
    pessoas = pessoas if pessoas is not None else load_pessoas()
    p = pessoas.get(nome)
    return p["email"] if p and p.get("email") else None


# ----------------------------------------------------------------------
# Reuniões (content/meetings/AAAA-MM-DD-<titulo>.json)
# ----------------------------------------------------------------------
MEETINGS_DIR = os.path.join(CONTENT_DIR, "meetings")
ISSUES_DIR = os.path.join(CONTENT_DIR, "issues")
TASKS_DIR = os.path.join(CONTENT_DIR, "tasks")
DIAS_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]


def slug(texto):
    sem_acento = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-")


def id_reuniao(caminho_ou_nome):
    """'content/meetings/2026-11-25-reuniao-ti.json' → 'r-2026-11-25-reuniao-ti' (âncora na página)."""
    return "r-" + os.path.basename(caminho_ou_nome)[:-len(".json")]


def salvar_reuniao(dados):
    """
    Grava uma reunião nova e devolve o caminho.
    dados: {titulo, data (AAAA-MM-DD), horario, participantes [nomes], issues [códigos], texto}
    """
    os.makedirs(MEETINGS_DIR, exist_ok=True)
    base = f"{dados['data']}-{slug(dados['titulo']) or 'reuniao'}"
    caminho, n = os.path.join(MEETINGS_DIR, f"{base}.json"), 2
    while os.path.exists(caminho):
        caminho, n = os.path.join(MEETINGS_DIR, f"{base}-{n}.json"), n + 1
    gravar_reuniao(caminho, dados)
    return caminho


def gravar_reuniao(caminho, dados):
    ordem = ["titulo", "data", "horario", "participantes", "issues", "texto", "email_enviado_em",
             "atualizada_em", "email_atualizacao_em",
             "cancelada_em", "motivo_cancelamento", "email_cancelamento_em"]
    saida = {k: dados[k] for k in ordem if k in dados}
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _ler_json(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def data_reuniao_br(iso):
    d = datetime.strptime(iso, "%Y-%m-%d").date()
    return f"{DIAS_SEMANA[d.weekday()]}, {d.strftime('%d/%m/%Y')}"


def assunto_reuniao(dados):
    """'Reunião Planejamento TI FFLCH - 25/11/2026 às 10h' (sem horário, só a data)."""
    data = datetime.strptime(dados["data"], "%Y-%m-%d").strftime("%d/%m/%Y")
    return f"{dados['titulo']} - {data}" + (f" às {dados['horario']}" if dados.get("horario") else "")


def email_reuniao(dados, caminho, atualizacao=False):
    """Assunto e corpo do e-mail de convocação (ou de reunião atualizada)."""
    nomes = [primeiro_nome(n) for n in dados.get("participantes", [])]
    saudacao = (", ".join(nomes[:-1]) + " e " + nomes[-1]) if len(nomes) > 1 else (nomes[0] if nomes else "Olá")
    quando = data_reuniao_br(dados["data"]) + (f", {dados['horario']}" if dados.get("horario") else "")

    # issues agrupadas por responsável, na ordem em que foram escolhidas
    grupos = {}
    for cod in dados.get("issues", []):
        issue = _ler_json(os.path.join(ISSUES_DIR, f"{cod}.json"))
        resp = (issue.get("responsavel") or "").strip() or "Outros assuntos"
        grupos.setdefault(resp, []).append(f"- {issue.get('descricao', f'{cod} (issue não encontrada)')}")

    if atualizacao:
        corpo = f"{saudacao},\n\nA reunião foi atualizada: {quando}, para tratarmos dos assuntos abaixo.\n"
    else:
        corpo = f"{saudacao},\n\nEstou agendando uma reunião {quando} para tratarmos dos assuntos abaixo.\n"
    if (dados.get("texto") or "").strip():
        corpo += f"\n{dados['texto'].strip()}\n"
    # "Outros assuntos" (issues sem responsável) sempre por último
    for resp, itens in sorted(grupos.items(), key=lambda g: g[0] == "Outros assuntos"):
        corpo += f"\n{resp}:\n" + "\n".join(itens) + "\n"
    corpo += ("\nA pauta está aberta: se quiserem incluir algum assunto, alterar ou retirar algum item, é só responder este e-mail antes da reunião, que eu farei a inclusão.\n\n"
              f"Reuniões: {SITE_URL}reunioes.html#{id_reuniao(caminho)}\n\n--\nThiago\nTI-FFLCH\n")
    assunto = ("ATUALIZADA: " if atualizacao else "") + assunto_reuniao(dados)
    return assunto, corpo


def email_cancelamento(dados, caminho):
    nomes = [primeiro_nome(n) for n in dados.get("participantes", [])]
    saudacao = (", ".join(nomes[:-1]) + " e " + nomes[-1]) if len(nomes) > 1 else (nomes[0] if nomes else "Olá")
    quando = data_reuniao_br(dados["data"]) + (f", {dados['horario']}" if dados.get("horario") else "")
    corpo = f"{saudacao},\n\nA reunião \"{dados['titulo']}\" de {quando} foi CANCELADA.\n"
    if (dados.get("motivo_cancelamento") or "").strip():
        corpo += f"\nMotivo: {dados['motivo_cancelamento'].strip()}\n"
    corpo += f"\nReuniões: {SITE_URL}reunioes.html#{id_reuniao(caminho)}\n\n--\nThiago\nTI-FFLCH\n"
    assunto = "CANCELADA: " + assunto_reuniao(dados)
    return assunto, corpo


def reunioes_agendadas():
    """[(caminho, dados)] das reuniões de hoje em diante que não foram canceladas, por data."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    out = []
    if os.path.isdir(MEETINGS_DIR):
        for f in sorted(os.listdir(MEETINGS_DIR)):
            if f.endswith(".json"):
                d = _ler_json(os.path.join(MEETINGS_DIR, f))
                if d.get("data", "") >= hoje and not d.get("cancelada_em"):
                    out.append((os.path.join(MEETINGS_DIR, f), d))
    return sorted(out, key=lambda x: (x[1]["data"], x[1].get("horario", "")))


CAMPOS_EDITAVEIS = ["titulo", "data", "horario", "participantes", "issues", "texto"]


def diferencas_reuniao(antes, depois):
    """Linhas legíveis com o que muda entre duas versões da reunião (para confirmar antes de gravar)."""
    def num(cod):
        return rotulo_issue(_ler_json(os.path.join(ISSUES_DIR, f"{cod}.json")))
    out = []
    for campo, rot in (("titulo", "Título"), ("data", "Data"), ("horario", "Horário"), ("texto", "Texto")):
        a, b = (antes.get(campo) or "").strip(), (depois.get(campo) or "").strip()
        if a != b:
            if campo == "data":
                a, b = data_reuniao_br(a), data_reuniao_br(b)
            if campo == "texto":
                out.append("Texto alterado:\n    " + (b.replace("\n", "\n    ") or "(vazio)"))
            else:
                out.append(f"{rot}: {a or '(vazio)'} → {b or '(vazio)'}")
    for campo, rot, fmt in (("participantes", "Participantes", str), ("issues", "Issues", num)):
        a, b = antes.get(campo, []), depois.get(campo, [])
        mais, menos = [x for x in b if x not in a], [x for x in a if x not in b]
        if mais:
            out.append(f"{rot} + " + ", ".join(fmt(x) for x in mais))
        if menos:
            out.append(f"{rot} − " + ", ".join(fmt(x) for x in menos))
    return out


def atualizar_reuniao(caminho, novos, padrao_email=False):
    """Grava os campos editados (mantém o arquivo, o link e o histórico de envios) e oferece o e-mail."""
    dados = _ler_json(caminho)
    dados.update({k: novos[k] for k in CAMPOS_EDITAVEIS if k in novos})
    dados["atualizada_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    gravar_reuniao(caminho, dados)
    print(f"✔ Reunião atualizada: {os.path.basename(caminho)}")
    oferecer_email_reuniao(caminho, padrao=padrao_email, atualizacao=True)


def cancelar_reuniao(caminho, motivo="", padrao_email=True):
    """Marca a reunião como cancelada e pergunta se avisa os participantes por e-mail."""
    dados = _ler_json(caminho)
    dados["cancelada_em"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    if motivo.strip():
        dados["motivo_cancelamento"] = motivo.strip()
    gravar_reuniao(caminho, dados)
    print(f"✔ Reunião cancelada: {os.path.basename(caminho)}")
    oferecer_email_reuniao(caminho, padrao=padrao_email, cancelamento=True)


def oferecer_email_reuniao(caminho, padrao=True, cancelamento=False, atualizacao=False):
    """Mostra o e-mail, pergunta se envia aos participantes e registra o envio no JSON."""
    dados = _ler_json(caminho)
    pessoas = load_pessoas()
    participantes = dados.get("participantes", [])
    destinatarios = [(n, email_de(n, pessoas)) for n in participantes]
    sem_email = [n for n, e in destinatarios if not e]
    if sem_email:
        print("ℹ Sem e-mail em pessoas.csv:", ", ".join(sem_email))
    if not any(e for _, e in destinatarios):
        print("⚠ Nenhum participante com e-mail — nada a enviar.")
        return False
    if cancelamento:
        assunto, corpo = email_cancelamento(dados, caminho)
    else:
        assunto, corpo = email_reuniao(dados, caminho, atualizacao=atualizacao)
    de = f"{REMETENTE_REUNIAO[0]} <{REMETENTE_REUNIAO[1]}>"
    print("\n--- E-mail " + "-" * 52 + f"\nDe: {de}\nAssunto: {assunto}\n\n{corpo}" + "-" * 63)
    if not perguntar_sim_nao(f"Disparar o e-mail para os {len(destinatarios) - len(sem_email)} participante(s)?", padrao):
        print("E-mail não enviado.")
        return False
    if enviar_email(destinatarios, assunto, corpo, remetente=REMETENTE_REUNIAO, conta=MSMTP_ACCOUNT_REUNIAO):
        campo = "email_cancelamento_em" if cancelamento else ("email_atualizacao_em" if atualizacao else "email_enviado_em")
        dados[campo] = datetime.now().strftime("%d/%m/%Y %H:%M")
        gravar_reuniao(caminho, dados)
        return True
    return False


# ----------------------------------------------------------------------
# Issues: número global sequencial ("numero": 1, 2, 3…) exibido como "#N".
# O arquivo continua <tarefa>-<n>.json, usado só internamente para as relações.
# ----------------------------------------------------------------------
def carregar_issues():
    """[(codigo, dados)] de todas as issues, em ordem de número."""
    out = []
    if os.path.isdir(ISSUES_DIR):
        for f in os.listdir(ISSUES_DIR):
            if f.endswith(".json"):
                out.append((f[:-5], _ler_json(os.path.join(ISSUES_DIR, f))))
    return sorted(out, key=lambda x: (x[1].get("numero") or 10**9, x[0]))


def proximo_numero_issue(reservados=()):
    usados = [d.get("numero") or 0 for _, d in carregar_issues()] + list(reservados)
    return max(usados, default=0) + 1


def rotulo_issue(dados_ou_numero):
    n = dados_ou_numero.get("numero") if isinstance(dados_ou_numero, dict) else dados_ou_numero
    return f"#{n}" if n else "#?"


def resolver_issue(ref):
    """'12', '#12' ou o código interno (dev005-3) → código interno; None se não existir."""
    ref = str(ref).strip().lstrip("#").replace(".json", "")
    for cod, d in carregar_issues():
        if (ref.isdigit() and d.get("numero") == int(ref)) or cod == ref:
            return cod
    return None


def com_numero(issue, numero):
    """Devolve a issue com "numero" como primeiro campo."""
    return {"numero": numero, **{k: v for k, v in issue.items() if k != "numero"}}


def escolher_issue_cli(incluir_fechadas=False, msg="Número da issue (#)"):
    """Lista as issues como '#N · tarefa → responsável | descrição' e devolve o código interno escolhido."""
    titulos = {}
    issues = [(c, d) for c, d in carregar_issues() if d.get("status") is True or incluir_fechadas]
    if not issues:
        print("Nenhuma issue encontrada.")
        return None
    print()
    for cod, d in issues:
        task = cod.rsplit("-", 1)[0]
        if task not in titulos:
            titulos[task] = titulo_tarefa(task)
        n = len(d.get("comentarios", []))
        extra = (" [fechada]" if d.get("status") is not True else "") + (f" 💬{n}" if n else "")
        print(f"{rotulo_issue(d):>5} · {titulos[task]} → {d.get('responsavel') or 'sem responsável'}{extra}")
        print(f"        {(d.get('descricao') or '')[:110]}")
    validos = {c for c, _ in issues}
    while True:
        cod = resolver_issue(input(f"\n{msg}: "))
        if cod in validos:
            return cod
        print("Issue não encontrada nesta lista.")


def titulo_tarefa(codigo_task):
    return _ler_json(os.path.join(TASKS_DIR, f"{codigo_task}.json")).get("titulo", "")


# ----------------------------------------------------------------------
# Tarefas
# ----------------------------------------------------------------------
def responsaveis_da_tarefa(task):
    resp = task.get("responsaveis")
    if not resp:
        antigo = task.get("responsavel")
        resp = [antigo] if antigo else []
    if isinstance(resp, str):
        resp = [resp]
    return [r for r in resp if r and str(r).strip()]


def estagiarios_da_tarefa(task, somente_ativos=True):
    """
    Estagiários de uma tarefa. Formato atual: [{"nome": "...", "ativo": true}].
    Aceita também o formato legado (lista de strings, "Não Há").
    """
    est = task.get("estagiarios") or []
    if isinstance(est, (str, dict)):
        est = [est]
    nomes = []
    for e in est:
        if isinstance(e, dict):
            nome, ativo = (e.get("nome") or "").strip(), e.get("ativo", True) is not False
        else:
            nome, ativo = str(e).strip(), True
        if not nome or nome == "Não Há":
            continue
        if somente_ativos and not ativo:
            continue
        nomes.append(nome)
    return nomes


# ----------------------------------------------------------------------
# Interação no terminal
# ----------------------------------------------------------------------
def perguntar_sim_nao(msg, padrao=False):
    sufixo = "[S/n]" if padrao else "[s/N]"
    resp = input(f"{msg} {sufixo} ").strip().lower()
    if not resp:
        return padrao
    return resp in ("s", "sim", "y", "yes")


def editar_no_editor(texto):
    """Abre o texto no $EDITOR (padrão: vim/nano) e devolve o conteúdo salvo."""
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or (
        "vim" if shutil.which("vim") else "nano")
    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(texto)
        caminho = tmp.name
    try:
        subprocess.run([editor, caminho])
        with open(caminho, encoding="utf-8") as f:
            return f.read().strip()
    finally:
        os.remove(caminho)


def ler_texto_multilinha(msg):
    print(f"{msg} (linha vazia para terminar):")
    linhas = []
    while True:
        linha = input("> ")
        if not linha.strip():
            break
        linhas.append(linha)
    return "\n".join(linhas).strip()


# ----------------------------------------------------------------------
# E-mail (msmtp)
# ----------------------------------------------------------------------
def enviar_email(destinatarios, assunto, corpo, remetente=None, conta=None):
    """
    Envia um e-mail texto puro via msmtp. destinatarios: lista de (nome, email).
    remetente: (nome, email) do cabeçalho From (padrão: TI FFLCH <fflchsti@usp.br>);
    conta: conta do ~/.msmtprc (padrão: MSMTP_ACCOUNT).
    """
    nome_rem, email_rem = remetente or (NOME_REMETENTE, EMAIL_REMETENTE)
    destinatarios = [(n, e) for n, e in destinatarios if e]
    if not destinatarios:
        print("⚠ Nenhum destinatário com e-mail cadastrado em pessoas.csv.")
        return False
    if not shutil.which("msmtp"):
        print("⚠ msmtp não encontrado no PATH; e-mail não enviado.")
        return False

    para = ", ".join(formataddr((str(Header(n, "utf-8")), e)) for n, e in destinatarios)
    mensagem = (
        f"From: {formataddr((str(Header(nome_rem, 'utf-8')), email_rem))}\n"
        + (f"Reply-To: {email_rem}\n" if remetente else "") +
        f"To: {para}\n"
        f"Subject: {Header(assunto, 'utf-8').encode()}\n"
        f"Date: {formatdate(localtime=True)}\n"
        f"Message-ID: {make_msgid(domain='usp.br')}\n"
        "MIME-Version: 1.0\n"
        "Content-Type: text/plain; charset=utf-8\n"
        "Content-Transfer-Encoding: 8bit\n"
        "\n"
        f"{corpo}\n"
    )
    proc = subprocess.run(
        ["msmtp", "-a", conta or MSMTP_ACCOUNT, "-t"],
        input=mensagem.encode("utf-8"),
        capture_output=True,
    )
    if proc.returncode != 0:
        print("⚠ Falha ao enviar e-mail:", proc.stderr.decode("utf-8", "replace").strip())
        return False
    print("✉ E-mail enviado para:", ", ".join(e for _, e in destinatarios))
    return True


def oferecer_aviso_email(nomes, montar_aviso):
    """
    Pergunta se deve avisar as pessoas por e-mail e, se sim, envia um e-mail para cada uma.
    montar_aviso: função nome -> (assunto, corpo).
    """
    pessoas = load_pessoas()
    nomes = [n for n in dict.fromkeys(nomes) if n]
    if not nomes:
        return
    com_email = [n for n in nomes if email_de(n, pessoas)]
    sem_email = [n for n in nomes if n not in com_email]
    if sem_email:
        print("ℹ Sem e-mail em pessoas.csv:", ", ".join(sem_email))
    if not com_email:
        return
    if not perguntar_sim_nao(f"\nAvisar por e-mail ({', '.join(com_email)})?"):
        return
    for nome in com_email:
        assunto, corpo = montar_aviso(nome)
        enviar_email([(nome, email_de(nome, pessoas))], assunto, corpo)


def primeiro_nome(nome):
    return nome.split()[0] if nome else ""


# ----------------------------------------------------------------------
# Ajuda do Claude para redigir issues
# ----------------------------------------------------------------------
SYSTEM_ISSUE = (
    "Você ajuda a equipe de TI da FFLCH-USP a registrar issues (pendências) ligadas a "
    "atividades. O usuário vai colar um rascunho mal formado, às vezes com erros de "
    "digitação, abreviações ou frases soltas. Reescreva-o como a descrição de uma issue: "
    "português do Brasil, claro, objetivo e técnico, em uma ou poucas frases curtas; se houver "
    "vários passos, separe-os com ' - ' na mesma linha. Preserve todos os fatos, nomes de "
    "sistemas, hosts, comandos, números e links do rascunho; não invente informação nem "
    "acrescente passos que não estão lá. Responda somente com o texto final da descrição, "
    "sem aspas, sem markdown e sem comentários."
)


def _prompt_issue(rascunho, contexto, instrucao_extra):
    partes = []
    if contexto:
        partes.append(f"<atividade>\n{contexto}\n</atividade>")
    partes.append(f"<rascunho>\n{rascunho}\n</rascunho>")
    if instrucao_extra:
        partes.append(f"<ajuste_pedido>\n{instrucao_extra}\n</ajuste_pedido>")
    return "\n\n".join(partes)


def _claude_via_sdk(prompt):
    import anthropic  # opcional: pip install anthropic

    client = anthropic.Anthropic()
    resposta = client.beta.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "low"},
        system=SYSTEM_ISSUE,
        messages=[{"role": "user", "content": prompt}],
    )
    if resposta.stop_reason == "refusal":
        raise RuntimeError("o Claude recusou o pedido")
    return "".join(b.text for b in resposta.content if b.type == "text").strip()


def _claude_via_cli(prompt):
    proc = subprocess.run(
        ["claude", "-p", "--model", CLAUDE_MODEL, "--tools", "",
         "--append-system-prompt", SYSTEM_ISSUE],
        input=prompt,
        capture_output=True,
        text=True,
        cwd=tempfile.gettempdir(),  # evita carregar o contexto do repositório
        timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "falha ao executar `claude -p`")
    return proc.stdout.strip()


def _sdk_disponivel():
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def chamar_claude(rascunho, contexto="", instrucao_extra=""):
    """Usa o SDK anthropic se houver credenciais; senão, o CLI `claude -p` (Claude Code)."""
    prompt = _prompt_issue(rascunho, contexto, instrucao_extra)
    if _sdk_disponivel():
        return _claude_via_sdk(prompt)
    if shutil.which("claude"):
        return _claude_via_cli(prompt)
    raise RuntimeError("nem o pacote `anthropic` (com ANTHROPIC_API_KEY) nem o CLI `claude` estão disponíveis")


def redigir_descricao(contexto="", texto_atual=""):
    """
    Fluxo interativo de descrição de issue.
    Pergunta se o usuário quer ajuda do Claude; se sim, recebe o rascunho, mostra a versão
    reescrita e só aceita após revisão. Retorna a descrição final (ou None se cancelado).
    """
    if not perguntar_sim_nao("\nQuer ajuda do Claude para redigir a descrição?"):
        if texto_atual:
            novo = input("Nova descrição (Enter mantém a atual): ").strip()
            return novo or texto_atual
        return input("\nDescrição da issue: ").strip()

    if texto_atual:
        print(f"\nDescrição atual:\n  {texto_atual}\n")
        rascunho = ler_texto_multilinha("Digite o rascunho (Enter direto usa a descrição atual)") or texto_atual
    else:
        rascunho = ler_texto_multilinha("\nDigite o rascunho da issue, do jeito que vier")
    if not rascunho:
        print("Rascunho vazio.")
        return None

    instrucao = ""
    while True:
        print("\n⏳ Consultando o Claude...")
        try:
            proposta = chamar_claude(rascunho, contexto, instrucao)
        except Exception as e:
            print(f"⚠ Não foi possível usar o Claude: {e}")
            return editar_no_editor(rascunho) or None

        print("\n--- Proposta do Claude " + "-" * 40)
        print(proposta)
        print("-" * 63)
        opcao = input("[a]ceitar  [e]ditar no editor  [r]efazer com instrução  "
                      "[o]riginal (usar rascunho)  [c]ancelar: ").strip().lower()
        if opcao == "a":
            return proposta
        if opcao == "e":
            return editar_no_editor(proposta) or None
        if opcao == "r":
            instrucao = input("O que ajustar? ").strip()
            continue
        if opcao == "o":
            return rascunho
        if opcao == "c":
            return None


# ----------------------------------------------------------------------
# Textos dos avisos de atribuição
# ----------------------------------------------------------------------
def _assinatura():
    return f"Planejamento da TI-FFLCH: {SITE_URL}\n\n--\nTI FFLCH\n"


def aviso_issue(nome, task_codigo, task_titulo, issue_rotulo, descricao, data, reatribuicao=False):
    """issue_rotulo: '#N' (número global da issue)."""
    assunto = f"[TI-FFLCH] Issue {issue_rotulo} atribuída a você"
    acao = "foi reatribuída a você" if reatribuicao else "foi atribuída a você"
    corpo = (
        f"Olá {primeiro_nome(nome)},\n\n"
        f"A issue {issue_rotulo} {acao}.\n\n"
        f"Atividade: {task_titulo}\n"
        f"Issue: {issue_rotulo}\n"
        f"Data: {data}\n\n"
        f"Descrição:\n{descricao}\n\n"
        f"Detalhes da atividade: {SITE_URL}#{task_codigo}\n"
        f"{_assinatura()}"
    )
    return assunto, corpo


def aviso_tarefa(nome, task_codigo, task_titulo, papel):
    assunto = f"[TI-FFLCH] Atividade {task_titulo} atribuída a você"
    corpo = (
        f"Olá {primeiro_nome(nome)},\n\n"
        f"Você foi incluído(a) como {papel} da atividade {task_titulo}.\n\n"
        f"Detalhes da atividade: {SITE_URL}#{task_codigo}\n"
        f"{_assinatura()}"
    )
    return assunto, corpo


def aviso_comentarios(nome, itens):
    """
    E-mail com comentários novos em issues de uma pessoa.
    itens: lista de (issue_rotulo '#N', task_codigo, task_titulo, descricao_issue, [textos])
    """
    total = sum(len(i[4]) for i in itens)
    if len(itens) == 1:
        assunto = f"[TI-FFLCH] Comentário na issue {itens[0][0]}" if total == 1 else \
                  f"[TI-FFLCH] {total} comentários na issue {itens[0][0]}"
    else:
        assunto = f"[TI-FFLCH] {total} comentários em {len(itens)} issues"
    blocos = []
    for issue, task, titulo, descricao, textos in itens:
        coment = "\n".join(f"  > {t}".replace("\n", "\n  > ") for t in textos)
        blocos.append(
            f"Issue {issue} ({titulo})\n"
            f"  {descricao}\n\n"
            f"Comentário{'s' if len(textos) > 1 else ''}:\n{coment}\n\n"
            f"  {SITE_URL}#{task}"
        )
    corpo = (
        f"Olá {primeiro_nome(nome)},\n\n"
        f"{'Há comentários novos' if total > 1 else 'Há um comentário novo'} em issue sob sua responsabilidade:\n\n"
        + "\n\n----\n\n".join(blocos)
        + f"\n\n{_assinatura()}"
    )
    return assunto, corpo
