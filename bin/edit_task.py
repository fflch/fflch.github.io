"""
Edita as pessoas de uma tarefa:
- adicionar/remover responsáveis
- adicionar estagiários e marcar estagiários como ativos/inativos
  (estagiário inativo continua no JSON para histórico, mas não aparece no site)
"""
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import load_pessoas, oferecer_aviso_email, aviso_tarefa  # noqa: E402

TASKS_DIR = os.path.join(BASE_DIR, "content", "tasks")


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def salvar(caminho, data):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def escolher_indice(n, msg):
    while True:
        val = input(msg).strip()
        if not val:
            return None
        if val.isdigit() and 0 < int(val) <= n:
            return int(val) - 1
        print("Entrada inválida.")


def escolher_task():
    tasks = sorted(f for f in os.listdir(TASKS_DIR) if f.endswith(".json"))
    while True:
        cod = input("\nCódigo da tarefa (ex: dev005): ").strip().replace(".json", "")
        if f"{cod}.json" in tasks:
            return cod
        print("Tarefa não encontrada.")


def normalizar_estagiarios(task):
    est = task.get("estagiarios") or []
    out = []
    for e in est:
        if isinstance(e, dict):
            out.append({"nome": e.get("nome", ""), "ativo": e.get("ativo", True) is not False})
        elif e and e != "Não Há":
            out.append({"nome": e, "ativo": True})
    return out


def mostrar(task, codigo):
    print(f"\n{codigo} | {task.get('titulo', '')}")
    print("Responsáveis:")
    for i, r in enumerate(task["responsaveis"], 1):
        print(f"  {i} - {r}")
    print("Estagiários:")
    for i, e in enumerate(task["estagiarios"], 1):
        print(f"  {i} - {e['nome']} [{'ativo' if e['ativo'] else 'INATIVO'}]")


def main():
    codigo = escolher_task()
    caminho = os.path.join(TASKS_DIR, f"{codigo}.json")
    task = carregar(caminho)
    task["responsaveis"] = [r for r in (task.get("responsaveis") or []) if r]
    task["estagiarios"] = normalizar_estagiarios(task)
    pessoas = load_pessoas()
    novos = {}

    while True:
        mostrar(task, codigo)
        print("\n[1] adicionar responsável  [2] remover responsável  "
              "[3] adicionar estagiário  [4] ativar/inativar estagiário  [s] salvar  [q] sair sem salvar")
        op = input("> ").strip().lower()

        if op == "1":
            lista = [p["nome"] for p in pessoas.values()
                     if p["vinculo"] == "servidor" and p["ativo"] and p["nome"] not in task["responsaveis"]]
            for i, n in enumerate(lista, 1):
                print(f"  {i:02d} - {n}")
            idx = escolher_indice(len(lista), "Número (Enter cancela): ")
            if idx is not None:
                task["responsaveis"].append(lista[idx])
                novos[lista[idx]] = "responsável"
        elif op == "2":
            idx = escolher_indice(len(task["responsaveis"]), "Número do responsável a remover: ")
            if idx is not None:
                novos.pop(task["responsaveis"].pop(idx), None)
        elif op == "3":
            atuais = {e["nome"] for e in task["estagiarios"]}
            lista = [p["nome"] for p in pessoas.values()
                     if p["vinculo"] == "estagiario" and p["ativo"] and p["nome"] not in atuais]
            for i, n in enumerate(lista, 1):
                print(f"  {i:02d} - {n}")
            idx = escolher_indice(len(lista), "Número (Enter cancela): ")
            if idx is not None:
                task["estagiarios"].append({"nome": lista[idx], "ativo": True})
                novos[lista[idx]] = "estagiário(a)"
        elif op == "4":
            idx = escolher_indice(len(task["estagiarios"]), "Número do estagiário: ")
            if idx is not None:
                e = task["estagiarios"][idx]
                e["ativo"] = not e["ativo"]
                if e["ativo"]:
                    novos[e["nome"]] = "estagiário(a)"
                else:
                    novos.pop(e["nome"], None)
        elif op == "s":
            salvar(caminho, task)
            print(f"\n✔ Tarefa atualizada: {caminho}")
            if novos:
                titulo = task.get("titulo", "")
                oferecer_aviso_email(list(novos), lambda n: aviso_tarefa(n, codigo, titulo, novos[n]))
            return
        elif op == "q":
            print("Nada salvo.")
            return


if __name__ == "__main__":
    main()
