"""
Adiciona um comentário a uma issue. Comentários não têm autor: são anotações soltas,
gravadas no próprio JSON da issue em "comentarios": [{"data": "dd/mm/aaaa", "texto": "..."}].

    python3 bin/comment_issue.py        # escolhe a issue numa lista pelo número (#N)
    python3 bin/comment_issue.py 12     # comenta direto na issue #12

No fim, pergunta se deve avisar o responsável da issue por e-mail.
"""
import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import (  # noqa: E402
    load_pessoas, email_de, enviar_email, perguntar_sim_nao, ler_texto_multilinha, aviso_comentarios,
    escolher_issue_cli, resolver_issue, rotulo_issue,
)

ISSUES_DIR = os.path.join(BASE_DIR, "content", "issues")
TASKS_DIR = os.path.join(BASE_DIR, "content", "tasks")


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


def main():
    if len(sys.argv) > 1:
        codigo = resolver_issue(sys.argv[1])
        if not codigo:
            sys.exit(f"Issue {sys.argv[1]} não encontrada.")
    else:
        codigo = escolher_issue_cli(perguntar_sim_nao("Incluir issues fechadas na lista?"))
        if not codigo:
            return
    caminho = os.path.join(ISSUES_DIR, f"{codigo}.json")

    issue = carregar(caminho)
    task = codigo.rsplit("-", 1)[0]
    titulo = titulo_task(task)

    print(f"\nIssue {rotulo_issue(issue)} ({titulo})")
    print(f"Responsável: {issue.get('responsavel') or 'sem responsável'}")
    print(f"Descrição:   {issue.get('descricao', '')}")
    comentarios = issue.get("comentarios", [])
    if comentarios:
        print(f"\nComentários ({len(comentarios)}):")
        for c in comentarios:
            print(f"  [{c.get('data', '')}] {c.get('texto', '')}")

    texto = ler_texto_multilinha("\nComentário")
    if not texto:
        print("Nada a comentar.")
        return

    issue.setdefault("comentarios", []).append({"data": datetime.now().strftime("%d/%m/%Y"), "texto": texto})
    salvar(caminho, issue)
    print(f"\n✔ Comentário adicionado na issue {rotulo_issue(issue)}")

    nome = issue.get("responsavel") or ""
    pessoas = load_pessoas()
    email = email_de(nome, pessoas) if nome else None
    if not nome:
        print("ℹ A issue não tem responsável; nenhum e-mail a enviar.")
    elif not email:
        print(f"ℹ {nome} não tem e-mail em pessoas.csv.")
    elif perguntar_sim_nao(f"Enviar o comentário por e-mail para {nome} <{email}>?"):
        assunto, corpo = aviso_comentarios(nome, [(rotulo_issue(issue), task, titulo, issue.get("descricao", ""), [texto])])
        enviar_email([(nome, email)], assunto, corpo)


if __name__ == "__main__":
    main()
