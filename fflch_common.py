"""
Funções compartilhadas entre generate_site.py e os scripts de bin/:

- cadastro de pessoas (content/pessoas.csv)
- participantes das reuniões
- estagiários de uma tarefa (com a chave "ativo")
- envio de e-mail de atribuição via msmtp (conta fflchsti@usp.br)
- ajuda do Claude para redigir a descrição de uma issue
"""
import csv
import json
import os
import shutil
import subprocess
import tempfile
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
PESSOAS_CSV = os.path.join(CONTENT_DIR, "pessoas.csv")

SITE_URL = "https://fflch.github.io/"

# Conta do ~/.msmtprc usada para os avisos (from = fflchsti@usp.br)
MSMTP_ACCOUNT = "sti"
EMAIL_REMETENTE = "fflchsti@usp.br"
NOME_REMETENTE = "TI FFLCH"

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
# Reuniões
# ----------------------------------------------------------------------
def participantes_reuniao(tipo):
    """
    Lista de (nome, email) dos participantes de uma reunião.
    - Se existir content/meeting-<tipo>.csv (nome,email), usa o CSV.
    - A reunião "ti" não tem CSV: participam todos os servidores ativos de pessoas.csv.
    """
    caminho = os.path.join(CONTENT_DIR, f"meeting-{tipo}.csv")
    if os.path.exists(caminho):
        out = []
        with open(caminho, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if row and row[0].strip():
                    email = row[1].strip() if len(row) > 1 else ""
                    out.append((row[0].strip(), email))
        return out
    if tipo == "ti":
        return [(p["nome"], p["email"]) for p in pessoas_por_vinculo("servidor")]
    return []


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
def enviar_email(destinatarios, assunto, corpo):
    """Envia um e-mail texto puro via `msmtp -a sti`. destinatarios: lista de (nome, email)."""
    destinatarios = [(n, e) for n, e in destinatarios if e]
    if not destinatarios:
        print("⚠ Nenhum destinatário com e-mail cadastrado em pessoas.csv.")
        return False
    if not shutil.which("msmtp"):
        print("⚠ msmtp não encontrado no PATH; e-mail não enviado.")
        return False

    para = ", ".join(formataddr((str(Header(n, "utf-8")), e)) for n, e in destinatarios)
    mensagem = (
        f"From: {formataddr((NOME_REMETENTE, EMAIL_REMETENTE))}\n"
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
        ["msmtp", "-a", MSMTP_ACCOUNT, "-t"],
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


def aviso_issue(nome, task_codigo, task_titulo, issue_codigo, descricao, data, reatribuicao=False):
    assunto = f"[TI-FFLCH] Issue {issue_codigo} atribuída a você"
    acao = "foi reatribuída a você" if reatribuicao else "foi atribuída a você"
    corpo = (
        f"Olá {primeiro_nome(nome)},\n\n"
        f"A issue {issue_codigo} {acao}.\n\n"
        f"Atividade: {task_codigo} - {task_titulo}\n"
        f"Issue: {issue_codigo}\n"
        f"Data: {data}\n\n"
        f"Descrição:\n{descricao}\n\n"
        f"Detalhes da atividade: {SITE_URL}#{task_codigo}\n"
        f"{_assinatura()}"
    )
    return assunto, corpo


def aviso_tarefa(nome, task_codigo, task_titulo, papel):
    assunto = f"[TI-FFLCH] Atividade {task_codigo} atribuída a você"
    corpo = (
        f"Olá {primeiro_nome(nome)},\n\n"
        f"Você foi incluído(a) como {papel} da atividade {task_codigo} - {task_titulo}.\n\n"
        f"Detalhes da atividade: {SITE_URL}#{task_codigo}\n"
        f"{_assinatura()}"
    )
    return assunto, corpo


def aviso_comentarios(nome, itens):
    """
    E-mail com comentários novos em issues de uma pessoa.
    itens: lista de (issue_codigo, task_codigo, task_titulo, descricao_issue, [textos])
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
            f"Issue {issue} ({task} - {titulo})\n"
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
