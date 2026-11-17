"""
Lista os repositórios públicos e não arquivados das organizações fflch e uspdev
que NÃO estão associados a nenhuma tarefa.

    python3 bin/repos_sem_tarefa.py

Uma tarefa "cobre" um repositório quando o título ou a descrição dela cita "org/repo"
(ex: "uspdev/grafica", "https://github.com/fflch/ansible-role-tasks"), sem diferenciar maiúsculas.

A lista de repositórios públicos vem da API do GitHub, que não exige autenticação
(limite de 60 requisições/hora). Se o `gh` estiver logado, o token dele é usado
para ter um limite maior; a chave SSH não serve para a API.
"""
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_DIR = os.path.join(BASE_DIR, "content", "tasks")
ORGS = ["fflch", "uspdev"]  # ordem de exibição
PADRAO_REPO = re.compile(r"\b(fflch|uspdev)/([A-Za-z0-9_.-]+)", re.IGNORECASE)


def token_gh():
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    if shutil.which("gh"):
        try:
            r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return None


def repos_publicos(org, token):
    """Todos os repositórios públicos da organização (paginando de 100 em 100)."""
    repos, pagina = [], 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?type=public&per_page=100&page={pagina}"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "repos-sem-tarefa-script",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                lote = json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 403 and e.headers.get("X-RateLimit-Remaining") == "0":
                sys.exit("⚠ Limite da API do GitHub atingido. Faça `gh auth login` ou defina GITHUB_TOKEN e tente de novo.")
            raise
        repos += lote
        if len(lote) < 100:
            return repos
        pagina += 1


def repos_das_tarefas():
    """
    {"org/repo" (minúsculo): [(codigo, origem, ativa)]}, onde origem é "titulo" ou "descricao".
    Um repositório citado no título ou na descrição (inclusive em .tex) conta como em uso.
    """
    citados = {}
    for f in sorted(os.listdir(TASKS_DIR)):
        if not f.endswith(".json"):
            continue
        codigo = f[:-5]
        with open(os.path.join(TASKS_DIR, f), encoding="utf-8") as fh:
            t = json.load(fh)
        descricao = t.get("descricao", "") or ""
        if descricao.endswith(".tex"):
            caminho_tex = os.path.join(TASKS_DIR, f"{codigo}.tex")
            descricao = open(caminho_tex, encoding="utf-8").read() if os.path.exists(caminho_tex) else ""
        vistos = set()
        for origem, texto in (("titulo", t.get("titulo", "")), ("descricao", descricao)):
            for org, repo in PADRAO_REPO.findall(texto):
                chave = f"{org}/{repo.rstrip('.')}".lower()
                if chave in vistos:
                    continue
                vistos.add(chave)
                citados.setdefault(chave, []).append((codigo, origem, t.get("status") is True))
    return citados


def sugestao(chave, existentes):
    """Nome real provável para um "org/repo" citado que não existe: troca -/_ , outra org ou parecido."""
    org, nome = chave.split("/", 1)
    norm = lambda n: n.replace("_", "-")
    ativos = {k: r for k, r in existentes.items() if not r["archived"]}
    iguais = [k for k in ativos if norm(k.split("/", 1)[1]) == norm(nome)]
    iguais.sort(key=lambda k: k.split("/")[0] != org)  # mesma organização primeiro
    if iguais:
        return ativos[iguais[0]]["full_name"]
    parecidos = difflib.get_close_matches(chave, list(ativos), n=1, cutoff=0.85)
    return ativos[parecidos[0]]["full_name"] if parecidos else None


def normal(nome):
    """Compara nomes ignorando maiúsculas e tratando "-" e "_" como iguais."""
    return nome.lower().replace("_", "-")


def resolver(chave, indice):
    """
    Nome real (minúsculo) do repositório citado, ou None.
    Tenta o nome como está e, se não existir, corta sufixos ".algo" capturados por engano
    (ex: "uspdev/playbooks-sandbox-proaluno.As" no fim de uma frase).
    """
    candidato = chave
    while True:
        if normal(candidato) in indice:
            return indice[normal(candidato)]
        if "." not in candidato.split("/", 1)[1]:
            return None
        candidato = candidato.rsplit(".", 1)[0]


def main():
    token = token_gh()
    print("Consultando a API do GitHub" + (" (com token do gh)" if token else " (sem autenticação)") + "...\n")

    repos_por_org = {org: repos_publicos(org, token) for org in ORGS}
    existentes = {r["full_name"].lower(): r for repos in repos_por_org.values() for r in repos}
    indice = {normal(k): k for k in existentes}

    # cobertura: repositório real -> tarefas que o citam (título ou descrição)
    citados = repos_das_tarefas()
    cobertura = {}
    for chave, tarefas in citados.items():
        real = resolver(chave, indice)
        if real:
            cobertura.setdefault(real, []).extend(tarefas)

    total_sem = 0
    for org in ORGS:
        todos = repos_por_org[org]
        ativos = sorted((r for r in todos if not r["archived"]), key=lambda r: r["name"].lower())

        sem_tarefa, so_inativa = [], []
        for r in ativos:
            tarefas = cobertura.get(r["full_name"].lower(), [])
            if not tarefas:
                sem_tarefa.append(r)
            elif not any(ativa for _, _, ativa in tarefas):
                so_inativa.append((r, tarefas))
        total_sem += len(sem_tarefa)

        print("=" * 78)
        print(f"{org}: {len(ativos)} repositórios públicos não arquivados "
              f"({len(todos) - len(ativos)} arquivados ignorados) · {len(sem_tarefa)} sem tarefa")
        print("=" * 78)
        for r in sem_tarefa:
            print(f"  {r['full_name']}")
        if so_inativa:
            print(f"\n  Só têm tarefa INATIVA ({len(so_inativa)}):")
            for r, tarefas in so_inativa:
                print(f"  {r['full_name']:<45} → {', '.join(sorted({c for c, _, _ in tarefas}))}")
        print()

    # sentido inverso: títulos de tarefas ativas que citam repositórios inexistentes ou arquivados
    problemas = []
    for chave, tarefas in sorted(citados.items()):
        ativas = [c for c, origem, ativa in tarefas if ativa and origem == "titulo"]
        if not ativas:
            continue
        real = resolver(chave, indice)
        if real is None:
            sug = sugestao(chave, existentes)
            problemas.append((chave, ativas, f"não existe; você quis dizer {sug}?" if sug
                              else "não encontrado (privado, renomeado ou nome errado no título?)"))
        elif existentes[real]["archived"]:
            problemas.append((chave, ativas, "arquivado no GitHub"))
        elif real != chave:
            problemas.append((chave, ativas, f"o nome certo é {existentes[real]['full_name']}"))
    if problemas:
        print("=" * 78)
        print(f"Títulos de tarefas com repositório fora da lista ou com nome diferente ({len(problemas)})")
        print("=" * 78)
        for chave, ativas, motivo in problemas:
            print(f"  {chave:<45} {', '.join(ativas)} → {motivo}")
        print()

    print(f"Total de repositórios sem tarefa: {total_sem}")


if __name__ == "__main__":
    main()
