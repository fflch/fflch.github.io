"""
Housekeeping das issues abertas: percorre uma a uma, mostra o que tem e pergunta o que fazer.

    python3 bin/claude_housekeeping_issues.py          # todas as issues abertas
    python3 bin/claude_housekeeping_issues.py dev      # só as de tarefas que começam com "dev"

Para cada issue:
  [m]anter  → o Claude reescreve a descrição e ela abre no $EDITOR já melhorada
              (o texto original vai junto, em linhas com "#", que são descartadas)
  [f]echar  → fecha a issue (grava data_fechamento), com comentário opcional
  [p]ular   → segue para a próxima sem mexer
  [s]air    → encerra

O Claude já vai trabalhando nas próximas issues em segundo plano, para não ter espera.
"""
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import chamar_claude, editar_no_editor, perguntar_sim_nao, rotulo_issue  # noqa: E402

ISSUES_DIR = os.path.join(BASE_DIR, "content", "issues")
TASKS_DIR = os.path.join(BASE_DIR, "content", "tasks")
PREFETCH = 2  # quantas issues à frente o Claude já vai reescrevendo


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def salvar(caminho, data):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def ordem(nome_arquivo):
    tarefa, _, num = nome_arquivo[:-5].rpartition("-")
    return (tarefa, int(num) if num.isdigit() else 0)


def carregar_task(codigo_task):
    caminho = os.path.join(TASKS_DIR, f"{codigo_task}.json")
    return carregar(caminho) if os.path.exists(caminho) else {}


def contexto_da_task(codigo_task, task):
    desc = str(task.get("descricao", ""))
    if desc.endswith(".tex"):
        desc = ""
    return f"{task.get('titulo', '')}\n{desc}".strip()


def issues_abertas(prefixo=""):
    out = []
    for f in sorted((f for f in os.listdir(ISSUES_DIR) if f.endswith(".json")), key=ordem):
        if prefixo and not f.startswith(prefixo):
            continue
        data = carregar(os.path.join(ISSUES_DIR, f))
        if data.get("status") is True:
            out.append(f[:-5])
    return out


def melhorar(codigo):
    """Roda em thread: pede ao Claude uma versão melhorada da descrição."""
    issue = carregar(os.path.join(ISSUES_DIR, f"{codigo}.json"))
    task_cod = codigo.rsplit("-", 1)[0]
    descricao = issue.get("descricao", "").strip()
    if not descricao:
        return ""
    return chamar_claude(descricao, contexto_da_task(task_cod, carregar_task(task_cod)))


def mostrar(codigo, issue, task, pos, total):
    task_cod = codigo.rsplit("-", 1)[0]
    print("\n" + "=" * 70)
    print(f"[{pos}/{total}] Issue {rotulo_issue(issue)}  ({task.get('titulo', '')})")
    print(f"Responsável: {issue.get('responsavel') or 'sem responsável'}")
    print(f"Aberta em:   {issue.get('data', '?')}")
    print(f"Descrição:   {issue.get('descricao', '')}")
    comentarios = issue.get("comentarios", [])
    if comentarios:
        print(f"Comentários ({len(comentarios)}):")
        for c in comentarios:
            print(f"  [{c.get('data', '')}] {c.get('texto', '')}")
    print("=" * 70)


def texto_para_editor(proposta, original):
    linhas = [proposta, "", "# Edite a descrição acima. Linhas com '#' são ignoradas.",
              "# Deixe vazio para manter a descrição original.", "#", "# Original:"]
    linhas += [f"#   {l}" for l in original.splitlines()]
    return "\n".join(linhas) + "\n"


def limpar_editor(texto):
    return "\n".join(l for l in texto.splitlines() if not l.lstrip().startswith("#")).strip()


def manter(codigo, caminho, issue, futuro):
    original = issue.get("descricao", "")
    print("⏳ Aguardando o Claude..." if not futuro.done() else "", end="", flush=True)
    try:
        proposta = futuro.result() or original
    except Exception as e:
        print(f"\n⚠ Não foi possível usar o Claude: {e}")
        proposta = original
    print("\r" + " " * 30 + "\r", end="")

    if proposta.strip() == original.strip():
        print("ℹ O Claude não sugeriu mudanças.")
        if not perguntar_sim_nao("Abrir no editor mesmo assim?"):
            return
    else:
        print(f"Sugestão do Claude: {proposta}")
        input("Enter para abrir no editor... ")

    nova = limpar_editor(editar_no_editor(texto_para_editor(proposta, original)))
    if not nova or nova == original.strip():
        print("Descrição mantida como estava.")
        return
    issue["descricao"] = nova
    salvar(caminho, issue)
    print(f"✔ Issue {rotulo_issue(issue)} atualizada: {nova}")


def fechar(codigo, caminho, issue):
    comentario = input("Comentário de fechamento (Enter pula): ").strip()
    hoje = datetime.now().strftime("%d/%m/%Y")
    if comentario:
        issue.setdefault("comentarios", []).append({"data": hoje, "texto": comentario})
    issue["status"] = False
    issue["data_fechamento"] = hoje
    salvar(caminho, issue)
    print(f"✔ Issue {rotulo_issue(issue)} fechada.")


def main():
    prefixo = sys.argv[1] if len(sys.argv) > 1 else ""
    codigos = issues_abertas(prefixo)
    if not codigos:
        print("Nenhuma issue aberta.")
        return
    total = len(codigos)
    print(f"{total} issue(s) aberta(s){f' com prefixo {prefixo!r}' if prefixo else ''}.")

    contagem = {"mantidas": 0, "editadas": 0, "fechadas": 0, "puladas": 0}
    futuros = {}
    with ThreadPoolExecutor(max_workers=PREFETCH) as pool:
        def agendar(i):
            if i < total and codigos[i] not in futuros:
                futuros[codigos[i]] = pool.submit(melhorar, codigos[i])

        for i, codigo in enumerate(codigos):
            for j in range(i, i + PREFETCH + 1):
                agendar(j)

            caminho = os.path.join(ISSUES_DIR, f"{codigo}.json")
            issue = carregar(caminho)
            if issue.get("status") is not True:  # fechada por fora no meio do caminho
                continue
            task = carregar_task(codigo.rsplit("-", 1)[0])
            mostrar(codigo, issue, task, i + 1, total)

            while True:
                op = input("[m]anter e revisar  [f]echar  [p]ular  [s]air: ").strip().lower()
                if op in ("m", "f", "p", "s"):
                    break

            if op == "s":
                for f in futuros.values():
                    f.cancel()
                break
            if op == "p":
                contagem["puladas"] += 1
            elif op == "f":
                fechar(codigo, caminho, issue)
                contagem["fechadas"] += 1
            elif op == "m":
                antes = issue.get("descricao")
                manter(codigo, caminho, issue, futuros[codigo])
                contagem["editadas" if issue.get("descricao") != antes else "mantidas"] += 1

    print("\nResumo: " + ", ".join(f"{v} {k}" for k, v in contagem.items()))
    print("Lembre de rodar generate_site.py e commitar as mudanças.")


if __name__ == "__main__":
    main()
