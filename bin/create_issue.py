import os
import sys
import json
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import (  # noqa: E402
    responsaveis_da_tarefa, estagiarios_da_tarefa, redigir_descricao,
    oferecer_aviso_email, aviso_issue, proximo_numero_issue, com_numero, rotulo_issue,
)

TASKS_DIR = os.path.join(BASE_DIR, "content", "tasks")
ISSUES_DIR = os.path.join(BASE_DIR, "content", "issues")


# ----------------------------------------
# Lista tasks (somente ativas)
# ----------------------------------------
def listar_tasks():
    tasks = []
    for f in sorted(os.listdir(TASKS_DIR)):
        if not f.endswith(".json"):
            continue
        try:
            with open(os.path.join(TASKS_DIR, f), encoding="utf-8") as fh:
                if json.load(fh).get("status") is not True:
                    continue
        except Exception:
            pass
        tasks.append(f)
    return tasks


# ----------------------------------------
# Escolhe task
# ----------------------------------------
def escolher_task(tasks):
    print("\nTasks disponíveis:\n")

    for i, t in enumerate(tasks, 1):
        caminho = os.path.join(TASKS_DIR, t)

        try:
            with open(caminho, encoding="utf-8") as f:
                data = json.load(f)
                titulo = data.get("titulo", "Sem título")
        except Exception:
            titulo = "Erro ao ler"

        print(f"{i:03d} - {titulo}")

    while True:
        escolha = input("\nNúmero da tarefa: ").strip()

        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(tasks):
                return tasks[idx]

        if not escolha.endswith(".json"):
            escolha += ".json"
        if escolha in tasks:
            return escolha

        print("Entrada inválida.")


def carregar_task(nome_arquivo):
    caminho = os.path.join(TASKS_DIR, nome_arquivo)
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def extrair_responsaveis(task_data):
    """Funcionários + estagiários ativos da tarefa, sem duplicar."""
    return list(dict.fromkeys(responsaveis_da_tarefa(task_data) + estagiarios_da_tarefa(task_data)))


def escolher_responsavel(lista):
    print("\nResponsáveis disponíveis (funcionários + estagiários ativos):\n")

    for i, nome in enumerate(lista, 1):
        print(f"{i} - {nome}")

    while True:
        escolha = input("\nEscolha o responsável: ").strip()

        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(lista):
                return lista[idx]

        if escolha in lista:
            return escolha

        print("Entrada inválida.")


def proximo_arquivo_issue(prefixo):
    pattern = re.compile(rf"^{prefixo}-(\d+)\.json$")
    numeros = []

    os.makedirs(ISSUES_DIR, exist_ok=True)

    for f in os.listdir(ISSUES_DIR):
        match = pattern.match(f)
        if match:
            numeros.append(int(match.group(1)))

    return max(numeros) + 1 if numeros else 1


def contexto_da_task(prefixo, task_data):
    descricao = task_data.get("descricao", "")
    if descricao.endswith(".tex"):
        descricao = ""
    return f"{task_data.get('titulo', '')}\n{descricao}".strip()


def main():
    tasks = listar_tasks()
    task_file = escolher_task(tasks)

    task_data = carregar_task(task_file)

    prefixo = task_file.replace(".json", "")
    titulo = task_data.get("titulo", "")

    responsaveis = extrair_responsaveis(task_data)

    if not responsaveis:
        print("⚠ Task não possui responsáveis ou estagiários ativos.")
        return

    print(f"\nTarefa selecionada: {titulo}")

    responsavel = escolher_responsavel(responsaveis)

    descricao = redigir_descricao(contexto=contexto_da_task(prefixo, task_data))
    if not descricao:
        print("\nIssue não criada.")
        return

    codigo = f"{prefixo}-{proximo_arquivo_issue(prefixo)}"   # nome interno do arquivo
    path = os.path.join(ISSUES_DIR, f"{codigo}.json")
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    issue = com_numero({
        "status": True,
        "descricao": descricao,
        "data": data_hoje,
        "responsavel": responsavel
    }, proximo_numero_issue())

    with open(path, "w", encoding="utf-8") as f:
        json.dump(issue, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n✔ Issue {rotulo_issue(issue)} criada.")

    oferecer_aviso_email(
        [responsavel],
        lambda n: aviso_issue(n, prefixo, titulo, rotulo_issue(issue), descricao, data_hoje),
    )


if __name__ == "__main__":
    main()
