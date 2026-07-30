import os
import json
from datetime import datetime
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ISSUES_DIR = os.path.join(BASE_DIR, "tasks", "issues")
BACKUP = False
ADD_DATA_FECHAMENTO = True  # opcional


def listar_issues_abertas():
    issues = []

    if not os.path.exists(ISSUES_DIR):
        print("Pasta de issues não existe.")
        return issues

    for f in os.listdir(ISSUES_DIR):
        if not f.endswith(".json"):
            continue

        caminho = os.path.join(ISSUES_DIR, f)

        try:
            with open(caminho, encoding="utf-8") as file:
                data = json.load(file)

            if data.get("status") is True:
                issues.append((f, data))

        except Exception as e:
            print(f"Erro ao ler {f}: {e}")

    issues.sort()
    return issues


def escolher_issue(issues):
    print("\nIssues abertas:\n")

    for i, (nome, data) in enumerate(issues, 1):
        desc = data.get("descricao", "")[:60]
        resp = data.get("responsavel", "N/A")

        print(f"{i:03d} - {nome} → {resp} | {desc}")

    while True:
        escolha = input("\nEscolha a issue para fechar: ").strip()

        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(issues):
                return issues[idx][0]

        print("Entrada inválida.")


def fechar_issue(nome_arquivo):
    caminho = os.path.join(ISSUES_DIR, nome_arquivo)

    with open(caminho, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("status") is False:
        print("Issue já está fechada.")
        return

    if BACKUP:
        shutil.copy2(caminho, caminho + ".bak")

    data["status"] = False

    if ADD_DATA_FECHAMENTO:
        data["data_fechamento"] = datetime.now().strftime("%d/%m/%Y")

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✔ Issue fechada: {nome_arquivo}")


def main():
    issues = listar_issues_abertas()

    if not issues:
        print("Nenhuma issue aberta.")
        return

    nome = escolher_issue(issues)
    fechar_issue(nome)


if __name__ == "__main__":
    main()