"""
Aplica no repositório as mudanças feitas na página de acompanhamento
(docs/acompanhamento.html → botão "Baixar mudanças").

    python3 bin/aplicar_mudancas.py            # aplica os arquivos pendentes de content/mudancas/
    python3 bin/aplicar_mudancas.py arquivo.json   # copia o arquivo para content/mudancas/ e aplica os pendentes

Os arquivos baixados ficam versionados em content/mudancas/ e o controle do que já foi
aplicado (e quando) fica em content/mudancas/aplicadas.json, também versionado. Se houver
mudancas-*.json em ~/Downloads, o script oferece movê-los para a pasta antes.

Para cada issue do arquivo, pode haver uma ou mais destas mudanças:
- responsavel : atribui a outra pessoa ("" = sem responsável)
- descricao   : edita a descrição
- tarefa      : muda a issue de tarefa (ganha um novo código, ex: dev022-3 → dev010-5)
- fechar      : fecha a issue (status false + data_fechamento = dia em que foi marcada)
- comentarios : comentários novos (lista de textos), gravados em "comentarios" com a data

Também cria as issues novas ("nova": true) com o próximo código livre da tarefa.

Antes de gravar, mostra o plano e pede confirmação. Se a issue mudou no repositório
depois que a página foi gerada (conflito), pergunta o que fazer. No fim, oferece avisar
por e-mail quem recebeu issues novas e lembra de regenerar o site.
"""
import os
import re
import sys
import json
import shutil
import glob
from collections import defaultdict
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import (  # noqa: E402
    load_pessoas, email_de, enviar_email, perguntar_sim_nao, primeiro_nome, SITE_URL, aviso_comentarios,
)

ISSUES_DIR = os.path.join(BASE_DIR, "content", "issues")
TASKS_DIR = os.path.join(BASE_DIR, "content", "tasks")
MEETINGS_DIR = os.path.join(BASE_DIR, "content", "meetings")
MUDANCAS_DIR = os.path.join(BASE_DIR, "content", "mudancas")
CONTROLE = os.path.join(MUDANCAS_DIR, "aplicadas.json")
DOWNLOADS = os.path.expanduser("~/Downloads")


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def salvar(caminho, data):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def titulo_task(codigo):
    caminho = os.path.join(TASKS_DIR, f"{codigo}.json")
    return carregar(caminho).get("titulo", "") if os.path.exists(caminho) else ""


def proximo_codigo(task, reservados):
    padrao = re.compile(rf"^{re.escape(task)}-(\d+)\.json$")
    numeros = [int(m.group(1)) for f in os.listdir(ISSUES_DIR) if (m := padrao.match(f))]
    numeros += [int(c.rsplit("-", 1)[1]) for c in reservados if c.startswith(f"{task}-")]
    return f"{task}-{max(numeros) + 1 if numeros else 1}"


def data_br(iso):
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return datetime.now().strftime("%d/%m/%Y")


def curto(texto, n=70):
    texto = " ".join(str(texto).split())
    return texto if len(texto) <= n else texto[: n - 1] + "…"


def atualizar_reunioes(antigo, novo):
    """Atualiza referências da issue nas pautas de reunião (content/meetings/*.json)."""
    if not os.path.isdir(MEETINGS_DIR):
        return
    for f in os.listdir(MEETINGS_DIR):
        if not f.endswith(".json"):
            continue
        caminho = os.path.join(MEETINGS_DIR, f)
        dados = carregar(caminho)
        lista = dados.get("issues", [])
        if f"{antigo}.json" in lista:
            dados["issues"] = [f"{novo}.json" if x == f"{antigo}.json" else x for x in lista]
            salvar(caminho, dados)


def aplicar_arquivo(caminho_arquivo):
    """Aplica um arquivo de mudanças. Retorna "aplicado", "nada", "recusado" ou "invalido"."""
    arquivo = carregar(caminho_arquivo)
    if arquivo.get("tipo") != "mudancas-acompanhamento":
        print("⚠ Este arquivo não parece ter sido baixado da página de acompanhamento.")
        return "invalido"

    pessoas = load_pessoas()
    tarefas_existentes = {f[:-5] for f in os.listdir(TASKS_DIR) if f.endswith(".json")}

    plano = []  # (codigo, caminho, issue, depois, em)
    novas = []  # (depois, em)
    for m in arquivo.get("mudancas", []):
        if m.get("nova"):
            d = m.get("depois", {})
            if d.get("tarefa") not in tarefas_existentes or not (d.get("descricao") or "").strip():
                print(f"⚠ Nova issue inválida (tarefa {d.get('tarefa')!r}) — ignorada.")
            else:
                novas.append((d, m.get("em")))
            continue
        cod, antes, depois = m["issue"], m.get("antes", {}), dict(m.get("depois", {}))
        caminho = os.path.join(ISSUES_DIR, f"{cod}.json")
        if not depois:
            continue
        if not os.path.exists(caminho):
            print(f"⚠ {cod}: issue não existe mais (já movida ou apagada?) — ignorada.")
            continue
        issue = carregar(caminho)
        if issue.get("status") is not True:
            print(f"ℹ {cod}: já está fechada — ignorada.")
            continue

        # conflitos: o campo mudou no repositório depois que a página foi gerada
        for campo in ("responsavel", "descricao"):
            atual = (issue.get(campo) or "").strip()
            if campo in depois and (antes.get(campo) or "").strip() != atual:
                print(f"\n⚠ Conflito em {cod} ({campo}):")
                print(f"   no repositório agora: {curto(atual) or '(vazio)'}")
                print(f"   na página era:        {curto(antes.get(campo)) or '(vazio)'}")
                print(f"   você quer:            {curto(depois[campo]) or '(vazio)'}")
                if not perguntar_sim_nao("   Sobrescrever com o seu valor?"):
                    del depois[campo]
            elif campo in depois and depois[campo] == atual:
                del depois[campo]

        if depois.get("tarefa") and depois["tarefa"] not in tarefas_existentes:
            print(f"⚠ {cod}: tarefa {depois['tarefa']} não existe — mudança de tarefa ignorada.")
            del depois["tarefa"]
        if depois.get("responsavel") and depois["responsavel"] not in pessoas:
            print(f"ℹ {cod}: '{depois['responsavel']}' não está em pessoas.csv (será gravado mesmo assim).")

        if depois:
            plano.append((cod, caminho, issue, depois, m.get("em")))

    if not plano and not novas:
        print("\nNada a aplicar (mudanças já presentes no repositório).")
        return "nada"

    # códigos novos para issues que mudam de tarefa e para as issues novas
    reservados = []
    novos_codigos = {}
    for cod, _, _, depois, _ in plano:
        if depois.get("tarefa"):
            novo = proximo_codigo(depois["tarefa"], reservados)
            reservados.append(novo)
            novos_codigos[cod] = novo
    codigos_novas = []
    for d, _ in novas:
        novo = proximo_codigo(d["tarefa"], reservados)
        reservados.append(novo)
        codigos_novas.append(novo)

    if novas:
        print(f"\n{len(novas)} issue(s) nova(s):\n")
        for (d, _), novo in zip(novas, codigos_novas):
            print(f"  + {novo}  ({titulo_task(d['tarefa'])}) → {d.get('responsavel') or '(sem responsável)'}")
            print(f"      {curto(d['descricao'])}")
            for t in d.get("comentarios") or []:
                print(f"      💬 {curto(t)}")

    if plano:
        print(f"\n{len(plano)} issue(s) com mudanças:\n")
    for cod, _, issue, depois, em in plano:
        print(f"  {cod}  ({curto(issue.get('descricao', ''), 60)})")
        if "responsavel" in depois:
            print(f"      → responsável: {issue.get('responsavel') or '(ninguém)'} → {depois['responsavel'] or '(ninguém)'}")
        if "descricao" in depois:
            print(f"      → descrição:   {curto(depois['descricao'])}")
        if "tarefa" in depois:
            print(f"      → tarefa:      {cod.split('-')[0]} → {depois['tarefa']}  (novo código {novos_codigos[cod]})")
        if depois.get("fechar"):
            print(f"      → fechar       (data_fechamento {data_br(em)})")
        for t in depois.get("comentarios") or []:
            print(f"      💬 comentário: {curto(t)}")

    if not perguntar_sim_nao("\nAplicar todas?", padrao=True):
        print("Nada foi alterado.")
        return "recusado"

    atribuicoes = defaultdict(list)  # nome -> [(codigo_final, task, descricao, data)]
    comentados = defaultdict(list)   # nome -> [(codigo, task, titulo, descricao, [textos])]

    def novos_comentarios(lista, em):
        return [{"data": data_br(em), "texto": t.strip()} for t in (lista or []) if t and t.strip()]

    for (d, em), novo in zip(novas, codigos_novas):
        issue = {"status": True, "descricao": d["descricao"].strip(), "data": data_br(em),
                 "responsavel": d.get("responsavel") or ""}
        if novos_comentarios(d.get("comentarios"), em):
            issue["comentarios"] = novos_comentarios(d.get("comentarios"), em)
        salvar(os.path.join(ISSUES_DIR, f"{novo}.json"), issue)
        if issue["responsavel"]:
            atribuicoes[issue["responsavel"]].append((novo, d["tarefa"], issue["descricao"], issue["data"]))
        print(f"✔ criada {novo}")

    for cod, caminho, issue, depois, em in plano:
        if "descricao" in depois:
            issue["descricao"] = depois["descricao"]
        if "responsavel" in depois:
            issue["responsavel"] = depois["responsavel"]
        if depois.get("fechar"):
            issue["status"] = False
            issue["data_fechamento"] = data_br(em)
        comentarios = novos_comentarios(depois.get("comentarios"), em)
        if comentarios:
            issue.setdefault("comentarios", []).extend(comentarios)

        codigo_final = cod
        if cod in novos_codigos:
            codigo_final = novos_codigos[cod]
            salvar(os.path.join(ISSUES_DIR, f"{codigo_final}.json"), issue)
            os.remove(caminho)
            atualizar_reunioes(cod, codigo_final)
        else:
            salvar(caminho, issue)

        if depois.get("responsavel") and not depois.get("fechar"):
            atribuicoes[depois["responsavel"]].append(
                (codigo_final, codigo_final.split("-")[0], issue.get("descricao", ""), issue.get("data", "")))

        if comentarios and issue.get("responsavel"):
            task = codigo_final.rsplit("-", 1)[0]
            comentados[issue["responsavel"]].append(
                (codigo_final, task, titulo_task(task), issue.get("descricao", ""), [c["texto"] for c in comentarios]))

        print(f"✔ {cod}" + (f" → {codigo_final}" if codigo_final != cod else ""))

    # avisos por e-mail: um e-mail por pessoa com todas as issues que ela recebeu
    com_email = [n for n in atribuicoes if email_de(n, pessoas)]
    if com_email and perguntar_sim_nao(f"\nAvisar por e-mail quem recebeu issues ({', '.join(com_email)})?"):
        for nome in com_email:
            itens = atribuicoes[nome]
            linhas = "\n\n".join(
                f"- {c} ({t} - {titulo_task(t)}), aberta em {d}\n  {desc}\n  {SITE_URL}#{t}"
                for c, t, desc, d in itens)
            corpo = (
                f"Olá {primeiro_nome(nome)},\n\n"
                f"{'As issues abaixo foram atribuídas' if len(itens) > 1 else 'A issue abaixo foi atribuída'} a você:\n\n"
                f"{linhas}\n\n"
                f"Planejamento da TI-FFLCH: {SITE_URL}\n\n--\nTI FFLCH\n"
            )
            assunto = (f"[TI-FFLCH] {len(itens)} issues atribuídas a você" if len(itens) > 1
                       else f"[TI-FFLCH] Issue {itens[0][0]} atribuída a você")
            enviar_email([(nome, email_de(nome, pessoas))], assunto, corpo)

    # comentários: um e-mail por responsável com todos os comentários novos nas issues dele
    com_email = [n for n in comentados if email_de(n, pessoas)]
    sem_email = [n for n in comentados if n not in com_email]
    if sem_email:
        print("ℹ Sem e-mail em pessoas.csv (comentários não avisados):", ", ".join(sem_email))
    if com_email and perguntar_sim_nao(f"\nEnviar os comentários por e-mail para os responsáveis ({', '.join(com_email)})?"):
        for nome in com_email:
            assunto, corpo = aviso_comentarios(nome, comentados[nome])
            enviar_email([(nome, email_de(nome, pessoas))], assunto, corpo)

    return "aplicado"


# ----------------------------------------------------------------------
# Pasta de mudanças e controle do que já foi aplicado
# ----------------------------------------------------------------------
def carregar_controle():
    return carregar(CONTROLE) if os.path.exists(CONTROLE) else {}


def trazer_para_pasta(origem):
    destino = os.path.join(MUDANCAS_DIR, os.path.basename(origem))
    if os.path.abspath(origem) == os.path.abspath(destino):
        return
    if os.path.exists(destino):
        print(f"ℹ {os.path.basename(origem)} já está em content/mudancas/.")
        return
    shutil.copy2(origem, destino)
    print(f"✔ {os.path.basename(origem)} copiado para content/mudancas/")


def oferecer_downloads(controle):
    if not os.path.isdir(DOWNLOADS):
        return
    achados = sorted(f for f in glob.glob(os.path.join(DOWNLOADS, "mudancas-*.json"))
                     if not os.path.exists(os.path.join(MUDANCAS_DIR, os.path.basename(f)))
                     and os.path.basename(f) not in controle)
    if not achados:
        return
    print(f"Encontrei {len(achados)} arquivo(s) de mudanças em ~/Downloads:")
    for f in achados:
        print(f"  {os.path.basename(f)}")
    if perguntar_sim_nao("Mover para content/mudancas/?", padrao=True):
        for f in achados:
            shutil.move(f, os.path.join(MUDANCAS_DIR, os.path.basename(f)))
        print("✔ Movidos.")


def ordem_arquivo(caminho):
    try:
        return (carregar(caminho).get("gerado_em") or "", os.path.basename(caminho))
    except (OSError, ValueError):
        return ("", os.path.basename(caminho))


def main():
    os.makedirs(MUDANCAS_DIR, exist_ok=True)
    controle = carregar_controle()

    for origem in sys.argv[1:]:
        if not os.path.exists(origem):
            sys.exit(f"⚠ {origem} não existe.")
        trazer_para_pasta(origem)
    oferecer_downloads(controle)

    pendentes = sorted((f for f in glob.glob(os.path.join(MUDANCAS_DIR, "*.json"))
                        if os.path.basename(f) != os.path.basename(CONTROLE)
                        and os.path.basename(f) not in controle), key=ordem_arquivo)
    if not pendentes:
        print("Nenhum arquivo de mudanças pendente em content/mudancas/.")
        return

    print(f"\n{len(pendentes)} arquivo(s) pendente(s): " + ", ".join(os.path.basename(f) for f in pendentes))
    aplicou_algo = False
    for caminho in pendentes:
        nome = os.path.basename(caminho)
        print("\n" + "=" * 70 + f"\n{nome}\n" + "=" * 70)
        status = aplicar_arquivo(caminho)
        if status == "recusado":
            if perguntar_sim_nao(f"Descartar {nome} (marcar como tratado sem aplicar)?"):
                status = "descartado"
            else:
                print(f"{nome} continua pendente.")
                continue
        if status == "invalido":
            print(f"{nome} continua pendente (remova-o da pasta se não for um arquivo de mudanças).")
            continue
        controle[nome] = {"aplicado_em": datetime.now().strftime("%d/%m/%Y %H:%M"), "resultado": status}
        salvar(CONTROLE, dict(sorted(controle.items())))
        aplicou_algo = aplicou_algo or status == "aplicado"

    if aplicou_algo:
        print("\nPronto. Regenere o site (python3 generate_site.py) e faça commit/push"
              " (inclua content/mudancas/).")
        print("Ao reabrir a página, o navegador remove sozinho as mudanças já aplicadas.")


if __name__ == "__main__":
    main()
