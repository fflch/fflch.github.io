"""
Adiciona um comentário a uma issue. Comentários não têm autor: são anotações soltas,
gravadas no próprio JSON da issue em "comentarios": [{"data": "dd/mm/aaaa", "texto": "..."}].

    python3 bin/comment_issue.py            # escolhe a issue numa lista
    python3 bin/comment_issue.py dev022-2   # comenta direto nessa issue

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


def ordem(nome_arquivo):
    tarefa, _, num = nome_arquivo[:-5].rpartition("-")
    return (tarefa, int(num) if num.isdigit() else 0)


def escolher_issue():
    incluir_fechadas = perguntar_sim_nao("Incluir issues fechadas na lista?")
    issues = []
    for f in sorted((f for f in os.listdir(ISSUES_DIR) if f.endswith(".json")), key=ordem):
        data = carregar(os.path.join(ISSUES_DIR, f))
        if data.get("status") is True or incluir_fechadas:
            issues.append((f[:-5], data))
    if not issues:
        print("Nenhuma issue encontrada.")
        sys.exit(0)

    print()
    for i, (cod, data) in enumerate(issues, 1):
        n = len(data.get("comentarios", []))
        extra = (" [fechada]" if data.get("status") is not True else "") + (f" 💬{n}" if n else "")
        print(f"{i:03d} - {cod} → {data.get('responsavel') or 'sem responsável'}{extra} | {data.get('descricao', '')[:60]}")

    while True:
        escolha = input("\nNúmero ou código da issue: ").strip()
        if escolha.isdigit() and 0 < int(escolha) <= len(issues):
            return issues[int(escolha) - 1][0]
        if any(c == escolha for c, _ in issues):
            return escolha
        print("Entrada inválida.")


def main():
    codigo = sys.argv[1].replace(".json", "") if len(sys.argv) > 1 else escolher_issue()
    caminho = os.path.join(ISSUES_DIR, f"{codigo}.json")
    if not os.path.exists(caminho):
        print(f"Issue {codigo} não encontrada.")
        sys.exit(1)

    issue = carregar(caminho)
    task = codigo.rsplit("-", 1)[0]
    titulo = titulo_task(task)

    print(f"\n{codigo} ({task} - {titulo})")
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
    print(f"\n✔ Comentário adicionado em {codigo}")

    nome = issue.get("responsavel") or ""
    pessoas = load_pessoas()
    email = email_de(nome, pessoas) if nome else None
    if not nome:
        print("ℹ A issue não tem responsável; nenhum e-mail a enviar.")
    elif not email:
        print(f"ℹ {nome} não tem e-mail em pessoas.csv.")
    elif perguntar_sim_nao(f"Enviar o comentário por e-mail para {nome} <{email}>?"):
        assunto, corpo = aviso_comentarios(nome, [(codigo, task, titulo, issue.get("descricao", ""), [texto])])
        enviar_email([(nome, email)], assunto, corpo)


if __name__ == "__main__":
    main()
