import os
import csv
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SIGLAS_CSV = os.path.join(BASE_DIR, "files", "siglas.csv")
TASKS_DIR = os.path.join(BASE_DIR, "tasks")


def load_siglas():
    siglas = {}
    with open(SIGLAS_CSV, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            siglas[row["sigla"]] = row["significado"]
    return siglas


def escolher_sigla(siglas):
    print("\nSiglas disponíveis:\n")
    for i, (sigla, significado) in enumerate(siglas.items(), 1):
        print(f"{i:02d} - {sigla} → {significado}")

    while True:
        escolha = input("\nDigite a sigla ou número: ").strip()

        if escolha.isdigit():
            idx = int(escolha) - 1
            if 0 <= idx < len(siglas):
                return list(siglas.keys())[idx]

        if escolha in siglas:
            return escolha

        print("Entrada inválida, tente novamente.")


def proximo_numero(sigla):
    pattern = re.compile(rf"^{sigla}(\d+)\.json$")
    numeros = []

    os.makedirs(TASKS_DIR, exist_ok=True)

    for f in os.listdir(TASKS_DIR):
        match = pattern.match(f)
        if match:
            numeros.append(int(match.group(1)))

    return max(numeros) + 1 if numeros else 1


def input_lista(msg):
    print(f"{msg} (separar por vírgula ou deixar vazio)")
    val = input("> ").strip()
    if not val:
        return ["Não Há"]
    return [v.strip() for v in val.split(",")]


def main():
    siglas = load_siglas()

    sigla = escolher_sigla(siglas)
    significado = siglas[sigla]

    print(f"\nSelecionado: {sigla} → {significado}")

    numero = proximo_numero(sigla)
    filename = f"{sigla}{numero:03d}.json"
    path = os.path.join(TASKS_DIR, filename)

    print(f"Arquivo será: {filename}\n")

    # Inputs
    peso = input("Peso (default 1): ").strip() or "1"
    titulo = input("Título: ").strip()
    responsaveis = input_lista("Responsáveis")
    estagiarios = input_lista("Estagiários")
    descricao = input("Descrição (pode colar LaTeX): ").strip()

    data = {
        "status": True,
        "peso": int(peso),
        "titulo": titulo,
        "responsaveis": responsaveis,
        "estagiarios": estagiarios,
        "descricao": descricao
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✔ Arquivo criado: {path}")


if __name__ == "__main__":
    main()