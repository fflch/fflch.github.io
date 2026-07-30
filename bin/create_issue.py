import os
import json
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TASKS_DIR = os.path.join(BASE_DIR, "tasks")
ISSUES_DIR = os.path.join(TASKS_DIR, "issues")


# ----------------------------------------
# Lista tasks
# ----------------------------------------
def listar_tasks():
    tasks = []
    for f in os.listdir(TASKS_DIR):
        if f.endswith(".json"):
            tasks.append(f)
    tasks.sort()
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
        except:
            titulo = "Erro ao ler"

        print(f"{i:03d} - {t} → {titulo}")

    while True:
        escolha = input("\nDigite número ou nome da task: ").strip()

        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(tasks):
                return tasks[idx]

        if escolha in tasks:
            return escolha

        print("Entrada inválida.")


# ----------------------------------------
# Carrega task
# ----------------------------------------
def carregar_task(nome_arquivo):
    caminho = os.path.join(TASKS_DIR, nome_arquivo)
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------
# Extrai responsáveis (NOVO MODELO)
# ----------------------------------------
def extrair_responsaveis(task_data):

    resp = task_data.get("responsaveis")

    # compatibilidade com legado
    if not resp:
        antigo = task_data.get("responsavel")
        resp = [antigo] if antigo else []

    if isinstance(resp, str):
        resp = [resp]

    est = task_data.get("estagiarios", [])
    if isinstance(est, str):
        est = [est]

    est = [e for e in est if e and e != "Não Há"]

    # união sem duplicar
    return list(dict.fromkeys(resp + est))


# ----------------------------------------
# Escolhe responsável
# ----------------------------------------
def escolher_responsavel(lista):

    print("\nResponsáveis disponíveis (funcionários + estagiários):\n")

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


# ----------------------------------------
# Próximo número da issue
# ----------------------------------------
def proximo_numero_issue(prefixo):
    pattern = re.compile(rf"^{prefixo}-(\d+)\.json$")
    numeros = []

    os.makedirs(ISSUES_DIR, exist_ok=True)

    for f in os.listdir(ISSUES_DIR):
        match = pattern.match(f)
        if match:
            numeros.append(int(match.group(1)))

    return max(numeros) + 1 if numeros else 1


# ----------------------------------------
# MAIN
# ----------------------------------------
def main():
    tasks = listar_tasks()
    task_file = escolher_task(tasks)

    task_data = carregar_task(task_file)

    prefixo = task_file.replace(".json", "")
    titulo = task_data.get("titulo", "")

    responsaveis = extrair_responsaveis(task_data)

    if not responsaveis:
        print("⚠ Task não possui responsáveis ou estagiários.")
        return

    print(f"\nTask selecionada: {prefixo} → {titulo}")

    responsavel = escolher_responsavel(responsaveis)

    numero = proximo_numero_issue(prefixo)
    filename = f"{prefixo}-{numero}.json"
    path = os.path.join(ISSUES_DIR, filename)

    descricao = input("\nDescrição da issue: ").strip()
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    issue = {
        "status": True,
        "descricao": descricao,
        "data": data_hoje,
        "responsavel": responsavel
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(issue, f, indent=2, ensure_ascii=False)

    print(f"\n✔ Issue criada: {path}")


if __name__ == "__main__":
    main()