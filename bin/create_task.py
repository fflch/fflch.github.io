import os
import sys
import csv
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import load_pessoas, oferecer_aviso_email, aviso_tarefa  # noqa: E402

SIGLAS_CSV = os.path.join(BASE_DIR, "content", "siglas.csv")
TASKS_DIR = os.path.join(BASE_DIR, "content", "tasks")


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


def escolher_pessoas(titulo, vinculo):
    """Seleciona pessoas ativas de pessoas.csv pelo número (separados por vírgula)."""
    pessoas = [p["nome"] for p in load_pessoas().values() if p["vinculo"] == vinculo and p["ativo"]]
    print(f"\n{titulo}:")
    for i, nome in enumerate(pessoas, 1):
        print(f"  {i:02d} - {nome}")
    while True:
        val = input("Números separados por vírgula (Enter = nenhum): ").strip()
        if not val:
            return []
        try:
            idx = [int(x) - 1 for x in val.split(",") if x.strip()]
            if all(0 <= i < len(pessoas) for i in idx):
                return list(dict.fromkeys(pessoas[i] for i in idx))
        except ValueError:
            pass
        print("Entrada inválida.")


def main():
    siglas = load_siglas()

    sigla = escolher_sigla(siglas)
    significado = siglas[sigla]

    print(f"\nSelecionado: {sigla} → {significado}")

    numero = proximo_numero(sigla)
    codigo = f"{sigla}{numero:03d}"
    path = os.path.join(TASKS_DIR, f"{codigo}.json")

    print(f"Arquivo será: {codigo}.json\n")

    peso = input("Peso (default 1): ").strip() or "1"
    titulo = input("Título: ").strip()
    responsaveis = escolher_pessoas("Responsáveis (servidores)", "servidor")
    estagiarios = escolher_pessoas("Estagiários(as)", "estagiario")
    descricao = input("\nDescrição (pode colar LaTeX): ").strip()

    data = {
        "status": True,
        "peso": int(peso),
        "titulo": titulo,
        "responsaveis": responsaveis,
        "estagiarios": [{"nome": n, "ativo": True} for n in estagiarios],
        "descricao": descricao
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n✔ Arquivo criado: {path}")

    papel = {n: "responsável" for n in responsaveis}
    papel.update({n: "estagiário(a)" for n in estagiarios if n not in papel})
    oferecer_aviso_email(list(papel), lambda n: aviso_tarefa(n, codigo, titulo, papel[n]))


if __name__ == "__main__":
    main()
