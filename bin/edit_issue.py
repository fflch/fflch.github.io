"""
Edita uma issue existente: descrição (com ajuda opcional do Claude) e/ou responsável.

    python3 bin/edit_issue.py       # escolhe na lista pelo número (#N)
    python3 bin/edit_issue.py 12    # edita direto a issue #12
"""
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import (  # noqa: E402
    responsaveis_da_tarefa, estagiarios_da_tarefa, redigir_descricao,
    oferecer_aviso_email, aviso_issue, escolher_issue_cli, resolver_issue, rotulo_issue,
)

TASKS_DIR = os.path.join(BASE_DIR, "content", "tasks")
ISSUES_DIR = os.path.join(BASE_DIR, "content", "issues")


def carregar_json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def salvar_json(caminho, data):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def escolher(lista, rotulo, msg):
    for i, item in enumerate(lista, 1):
        print(f"{i:03d} - {rotulo(item)}")
    while True:
        escolha = input(f"\n{msg}: ").strip()
        if escolha.isdigit() and 0 < int(escolha) <= len(lista):
            return lista[int(escolha) - 1]
        print("Entrada inválida.")


def main():
    if len(sys.argv) > 1:
        codigo = resolver_issue(sys.argv[1])
        if not codigo:
            sys.exit(f"Issue {sys.argv[1]} não encontrada.")
    else:
        incluir_fechadas = input("Incluir issues fechadas na lista? [s/N] ").strip().lower() == "s"
        codigo = escolher_issue_cli(incluir_fechadas)
        if not codigo:
            return
    nome_arquivo = f"{codigo}.json"
    issue = carregar_json(os.path.join(ISSUES_DIR, nome_arquivo))
    task_codigo = codigo.rsplit("-", 1)[0]
    caminho_task = os.path.join(TASKS_DIR, f"{task_codigo}.json")
    task = carregar_json(caminho_task) if os.path.exists(caminho_task) else {}
    titulo = task.get("titulo", "")

    print(f"\nIssue {rotulo_issue(issue)} ({titulo})")
    print(f"  Responsável: {issue.get('responsavel') or 'N/A'}")
    print(f"  Descrição:   {issue.get('descricao', '')}")

    alterou = False
    reatribuido = None

    if input("\nAlterar a descrição? [s/N] ").strip().lower() == "s":
        contexto = f"{titulo}\n{task.get('descricao', '') if not str(task.get('descricao', '')).endswith('.tex') else ''}"
        nova = redigir_descricao(contexto=contexto.strip(), texto_atual=issue.get("descricao", ""))
        if nova and nova != issue.get("descricao"):
            issue["descricao"] = nova
            alterou = True

    if input("Alterar o responsável? [s/N] ").strip().lower() == "s":
        candidatos = list(dict.fromkeys(responsaveis_da_tarefa(task) + estagiarios_da_tarefa(task)))
        if not candidatos:
            print("⚠ A tarefa não tem responsáveis/estagiários ativos.")
        else:
            print()
            novo = escolher(candidatos, str, "Novo responsável")
            if novo != issue.get("responsavel"):
                issue["responsavel"] = novo
                reatribuido = novo
                alterou = True

    if not alterou:
        print("\nNada alterado.")
        return

    salvar_json(os.path.join(ISSUES_DIR, nome_arquivo), issue)
    print(f"\n✔ Issue {rotulo_issue(issue)} atualizada.")

    if reatribuido:
        oferecer_aviso_email(
            [reatribuido],
            lambda n: aviso_issue(n, task_codigo, titulo, rotulo_issue(issue), issue.get("descricao", ""),
                                  issue.get("data", ""), reatribuicao=True),
        )


if __name__ == "__main__":
    main()
