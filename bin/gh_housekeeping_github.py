"""
Levanta todos os repositórios das organizações fflch e uspdev (públicos, arquivados e privados)
e grava content/github.json, que o generate_site.py usa para montar docs/github.html.

    python3 bin/claude_housekeeping_github.py

Precisa do `gh` logado com acesso às organizações (os privados só aparecem assim). Por isso
o JSON é gerado nesta máquina e VERSIONADO: no deploy (GitHub Actions) só a página é montada.

Uma tarefa "cobre" um repositório quando o título ou a descrição dela (inclusive a guardada
em content/tasks/<codigo>.html) cita "org/repo"
(ex: "uspdev/grafica", "https://github.com/fflch/ansible-role-tasks"), sem diferenciar
maiúsculas e tratando "-" e "_" como iguais.

No terminal, avisa também sobre títulos de tarefas ativas que citam repositórios
inexistentes, arquivados ou com o nome escrito diferente.
"""
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fflch_common import descricao_da_tarefa, responsaveis_da_tarefa  # noqa: E402

TASKS_DIR = os.path.join(BASE_DIR, "content", "tasks")
SAIDA = os.path.join(BASE_DIR, "content", "github.json")
ORGS = ["fflch", "uspdev"]  # ordem de exibição
PADRAO_REPO = re.compile(r"\b(fflch|uspdev)/([A-Za-z0-9_.-]+)", re.IGNORECASE)

QUERY = """
query($org: String!, $cursor: String) {
  organization(login: $org) {
    repositories(first: 100, after: $cursor, orderBy: {field: NAME, direction: ASC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name nameWithOwner url isArchived isPrivate
        defaultBranchRef { name target { ... on Commit { committedDate } } }
      }
    }
  }
}
"""


# ----------------------------------------------------------------------
# GitHub (via gh)
# ----------------------------------------------------------------------
def gh_api(*args):
    proc = subprocess.run(["gh", "api", *args], capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def repos_da_org(org):
    repos, cursor = [], None
    while True:
        args = ["graphql", "-f", f"query={QUERY}", "-F", f"org={org}"]
        if cursor:
            args += ["-F", f"cursor={cursor}"]
        dados = gh_api(*args)["data"]["organization"]["repositories"]
        repos += dados["nodes"]
        if not dados["pageInfo"]["hasNextPage"]:
            return repos
        cursor = dados["pageInfo"]["endCursor"]


def top_commiters(full_name, n=3):
    """[(login, commits)] dos n maiores contribuidores (lista vazia para repositório vazio)."""
    try:
        contrib = gh_api(f"repos/{full_name}/contributors?per_page={n}") or []
    except RuntimeError:
        return []
    return [(c.get("login") or c.get("name") or "?", c.get("contributions", 0)) for c in contrib[:n]]


# ----------------------------------------------------------------------
# Tarefas
# ----------------------------------------------------------------------
def normal(nome):
    """Compara nomes ignorando maiúsculas e tratando "-" e "_" como iguais."""
    return nome.lower().replace("_", "-")


def carregar_tasks():
    tasks = {}
    for f in sorted(os.listdir(TASKS_DIR)):
        if f.endswith(".json"):
            with open(os.path.join(TASKS_DIR, f), encoding="utf-8") as fh:
                tasks[f[:-5]] = json.load(fh)
    return tasks


def repos_das_tarefas(tasks):
    """{"org/repo" (minúsculo): [(codigo, origem, ativa)]}, origem = "titulo" ou "descricao"."""
    citados = {}
    for codigo, t in tasks.items():
        # a descrição pode estar em content/tasks/<codigo>.html (ex: tarefas que agrupam vários
        # repositórios numa tabela); o "org/repo" é procurado no texto, inclusive nos links
        descricao = descricao_da_tarefa(codigo, t)
        vistos = set()
        for origem, texto in (("titulo", t.get("titulo", "")), ("descricao", descricao)):
            for org, repo in PADRAO_REPO.findall(texto):
                chave = f"{org}/{repo.rstrip('.')}".lower()
                if chave not in vistos:
                    vistos.add(chave)
                    citados.setdefault(chave, []).append((codigo, origem, t.get("status") is True))
    return citados


def resolver(chave, indice):
    """
    Nome real (minúsculo) do repositório citado, ou None. Se não existir como está, corta
    sufixos ".algo" capturados por engano (ex: "uspdev/repo.As" no fim de uma frase).
    """
    candidato = chave
    while True:
        if normal(candidato) in indice:
            return indice[normal(candidato)]
        if "." not in candidato.split("/", 1)[1]:
            return None
        candidato = candidato.rsplit(".", 1)[0]


def sugestao(chave, existentes):
    """Nome real provável para um "org/repo" citado que não existe."""
    org, nome = chave.split("/", 1)
    ativos = {k: r for k, r in existentes.items() if not r["isArchived"]}
    iguais = [k for k in ativos if normal(k.split("/", 1)[1]) == normal(nome)]
    iguais.sort(key=lambda k: k.split("/")[0] != org)
    if iguais:
        return ativos[iguais[0]]["nameWithOwner"]
    parecidos = difflib.get_close_matches(chave, list(ativos), n=1, cutoff=0.85)
    return ativos[parecidos[0]]["nameWithOwner"] if parecidos else None


def avisar_titulos(citados, indice, existentes):
    problemas = []
    for chave, tarefas in sorted(citados.items()):
        ativas = [c for c, origem, ativa in tarefas if ativa and origem == "titulo"]
        if not ativas:
            continue
        real = resolver(chave, indice)
        if real is None:
            sug = sugestao(chave, existentes)
            motivo = f"não existe; você quis dizer {sug}?" if sug else "não encontrado (renomeado ou nome errado?)"
        elif existentes[real]["isArchived"]:
            motivo = "arquivado no GitHub"
        elif real != chave:
            motivo = f"o nome certo é {existentes[real]['nameWithOwner']}"
        else:
            continue
        problemas.append((chave, ativas, motivo))
    if problemas:
        print(f"\nTítulos de tarefas com repositório fora da lista ou com nome diferente ({len(problemas)}):")
        for chave, ativas, motivo in problemas:
            print(f"  {chave:<45} {', '.join(ativas)} → {motivo}")


# ----------------------------------------------------------------------
def main():
    if not shutil.which("gh"):
        sys.exit("⚠ `gh` não encontrado. Instale e faça `gh auth login`.")

    print("Consultando o GitHub via gh...")
    repos_por_org = {org: repos_da_org(org) for org in ORGS}
    todos = [r for org in ORGS for r in repos_por_org[org]]
    existentes = {r["nameWithOwner"].lower(): r for r in todos}
    indice = {normal(k): k for k in existentes}

    print(f"Buscando os principais commiters de {len(todos)} repositórios...")
    with ThreadPoolExecutor(max_workers=8) as pool:
        commiters = dict(zip((r["nameWithOwner"] for r in todos),
                             pool.map(lambda r: top_commiters(r["nameWithOwner"]), todos)))

    tasks = carregar_tasks()
    citados = repos_das_tarefas(tasks)
    cobertura = {}
    for chave, lista in citados.items():
        real = resolver(chave, indice)
        if real:
            for codigo, _, ativa in lista:
                if codigo not in {c["codigo"] for c in cobertura.get(real, [])}:
                    t = tasks[codigo]
                    cobertura.setdefault(real, []).append({
                        "codigo": codigo,
                        "titulo": t.get("titulo", ""),
                        "ativa": ativa,
                        "responsaveis": responsaveis_da_tarefa(t),
                    })

    saida = {"gerado_em": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"), "repos": []}
    for r in todos:
        ref = r.get("defaultBranchRef") or {}
        situacao = "arquivado" if r["isArchived"] else ("privado" if r["isPrivate"] else "publico")
        saida["repos"].append({
            "org": r["nameWithOwner"].split("/")[0],
            "nome": r["nameWithOwner"],
            "url": r["url"],
            "situacao": situacao,
            "privado": r["isPrivate"],
            "branch": ref.get("name") or "",
            "ultimo_commit": (ref.get("target") or {}).get("committedDate") or "",
            "commiters": commiters.get(r["nameWithOwner"], []),
            "tarefas": cobertura.get(r["nameWithOwner"].lower(), []),
        })

    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=2, ensure_ascii=False)
        f.write("\n")

    for org in ORGS:
        rs = [r for r in saida["repos"] if r["org"] == org]
        pub = [r for r in rs if r["situacao"] == "publico"]
        sem = [r for r in pub if not r["tarefas"]]
        print(f"{org}: {len(rs)} repositórios ({len(pub)} públicos ativos, {len(sem)} deles sem tarefa)")
    avisar_titulos(citados, indice, existentes)
    print(f"\n✔ {os.path.relpath(SAIDA, BASE_DIR)} gerado. Commite-o; o deploy monta docs/github.html a partir dele.")


if __name__ == "__main__":
    main()
