import os
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
import shutil
import csv
from pathlib import Path
import markdown
import base64
import unicodedata
from jinja2 import Environment, FileSystemLoader

from fflch_common import (
    load_pessoas,
    id_reuniao,
    SITE_URL,
    responsaveis_da_tarefa,
    estagiarios_da_tarefa,
)

OUTPUT_DIR = "docs"
TASKS_DIR = os.path.join("content", "tasks")
ISSUES_DIR = os.path.join("content", "issues")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")
TUTORIAIS_DIR = os.path.join("content", "tutoriais")
ASSETS_DIR = "assets"
OUTPUT_TUTORIAIS = os.path.join(OUTPUT_DIR, "tutorial")
REPORTS_DIR = os.path.join("content", "reports")
OUTPUT_REPORTS = os.path.join(OUTPUT_DIR, "reports")
PAGES_DIR = os.path.join("content", "pages")
MEETINGS_DIR = os.path.join("content", "meetings")
OUTPUT_DOCS = "docs"
TEMPLATES_DIR = "templates"

# Mapeamento de extensões para linguagens do Prism.js
EXT_TO_LANG = {
    '.php': 'php',
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.html': 'markup',
    '.css': 'css',
    '.sh': 'bash',
    '.bash': 'bash',
    '.json': 'json',
    '.sql': 'sql',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.yml': 'yaml',
    '.yaml': 'yaml'
}

# Mapeamento de nomes exatos de arquivos sem extensão (ou especiais)
FILENAME_TO_LANG = {
    'dockerfile': 'dockerfile',
    'makefile': 'makefile',
    'jenkinsfile': 'groovy',
    'vagrantfile': 'ruby',
    '.gitignore': 'bash',
    '.env': 'bash',
    '.env.example': 'bash'
}

# Configuração do Jinja2
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=False
)


def latex_to_html(text):
    if not text:
        return ""

    text = text.replace("\\bigskip", "<br><br>")
    text = re.sub(r"\\textbf{([^}]*)}", r"<strong>\1</strong>", text)
    text = re.sub(r"\\textit{([^}]*)}", r"<em>\1</em>", text)
    text = text.replace("\\begin{itemize}", "<ul>")
    text = text.replace("\\end{itemize}", "</ul>")
    text = text.replace("\\item", "<li>")
    text = re.sub(r"\\url{([^}]*)}", r'<a href="\1" target="_blank">\1</a>', text)

    return text


jinja_env.filters['latex_to_html'] = latex_to_html
# Versão do build, usada como ?v= nos links de CSS para evitar CSS antigo em cache no navegador
jinja_env.globals["build_id"] = datetime.now().strftime("%Y%m%d%H%M%S")


def copy_assets():
    destino = os.path.join(OUTPUT_DIR, "assets")

    if os.path.exists(destino):
        shutil.rmtree(destino)

    if os.path.exists(ASSETS_DIR):
        shutil.copytree(ASSETS_DIR, destino)


def carregar_logo_base64():
    caminho_logo = os.path.join(ASSETS_DIR, "fflch.png")
    if os.path.exists(caminho_logo):
        with open(caminho_logo, "rb") as img_file:
            return "data:image/png;base64," + base64.b64encode(img_file.read()).decode('utf-8')
    return ""


def extrair_titulo_md(conteudo_md, nome_arquivo_padrao):
    """Extrai o título do Front Matter (--- title: Titulo ---) ou do primeiro header H1 (# Titulo)."""
    match_yaml = re.search(r"^---\s*\ntitle:\s*(.*?)\n---", conteudo_md, re.MULTILINE | re.IGNORECASE)
    if match_yaml:
        return match_yaml.group(1).strip()

    match_h1 = re.search(r"^#\s+(.*)", conteudo_md, re.MULTILINE)
    if match_h1:
        return match_h1.group(1).strip()

    return nome_arquivo_padrao.replace("-", " ").replace("_", " ").title()


def resolver_includes_html(conteudo_md):
    """
    Substitui [[include_html:caminho/arquivo.html]] pelo conteúdo HTML bruto
    lido da pasta assets/. Permite que o HTML seja renderizado diretamente no Markdown.
    """
    def substituidor(match):
        caminho_relativo = match.group(1).strip()
        caminho_asset = os.path.join(ASSETS_DIR, caminho_relativo)

        if os.path.exists(caminho_asset):
            try:
                with open(caminho_asset, 'r', encoding='utf-8') as f:
                    conteudo_html = f.read()
                return f"\n\n{conteudo_html}\n\n"
            except Exception as e:
                return f"\n*Erro ao ler include HTML {caminho_relativo}: {e}*\n"
        else:
            return f"\n*Arquivo HTML não encontrado: assets/{caminho_relativo}*\n"

    return re.sub(r"\[\[include_html:\s*(.*?)\s*\]\]", substituidor, conteudo_md)


def resolver_includes_assets(conteudo_md):
    """
    Substitui [[include:caminho/arquivo.ext]] pelo bloco de código markdown correspondente
    lido da pasta assets/. Trata subpastas, nomes especiais (como Dockerfile) e
    usa 'bash' como linguagem padrão se não identificar a extensão.
    """
    def substituidor(match):
        caminho_relativo = match.group(1).strip()
        caminho_asset = os.path.join(ASSETS_DIR, caminho_relativo)

        if os.path.exists(caminho_asset):
            nome_arquivo = os.path.basename(caminho_relativo).lower()
            ext = os.path.splitext(nome_arquivo)[1].lower()

            if nome_arquivo in FILENAME_TO_LANG:
                lang = FILENAME_TO_LANG[nome_arquivo]
            elif ext in EXT_TO_LANG:
                lang = EXT_TO_LANG[ext]
            else:
                lang = 'bash'

            try:
                with open(caminho_asset, 'r', encoding='utf-8') as f:
                    codigo = f.read()
                return f"\n```{lang}\n{codigo}\n```\n"
            except Exception as e:
                return f"\n*Erro ao ler include {caminho_relativo}: {e}*\n"
        else:
            return f"\n*Arquivo de include não encontrado: assets/{caminho_relativo}*\n"

    return re.sub(r"\[\[include:\s*(.*?)\s*\]\]", substituidor, conteudo_md)


def processar_relatorios():
    """Lê a pasta content/reports, processa includes, converte para HTML e gera lista alfabética."""
    if not os.path.exists(REPORTS_DIR):
        return []

    os.makedirs(OUTPUT_REPORTS, exist_ok=True)
    relatorios = []
    logo_base64 = carregar_logo_base64()
    template = jinja_env.get_template("report.html")

    for arquivo in sorted(os.listdir(REPORTS_DIR)):
        if arquivo.endswith(".md"):
            caminho_md = os.path.join(REPORTS_DIR, arquivo)
            nome_base = os.path.splitext(arquivo)[0]
            arquivo_html_nome = f"{nome_base}.html"
            caminho_html_destino = os.path.join(OUTPUT_REPORTS, arquivo_html_nome)

            with open(caminho_md, "r", encoding="utf-8") as f:
                conteudo_md = f.read()

            titulo = extrair_titulo_md(conteudo_md, nome_base)
            conteudo_md_limpo = re.sub(r"^---\s*\ntitle:.*?\n---\s*\n", "", conteudo_md, flags=re.MULTILINE | re.DOTALL)

            if "[TOC]" not in conteudo_md_limpo and "[toc]" not in conteudo_md_limpo:
                conteudo_md_limpo = f"[TOC]\n\n" + conteudo_md_limpo

            conteudo_md_processado = resolver_includes_assets(conteudo_md_limpo)

            html_corpo = markdown.markdown(
                conteudo_md_processado,
                extensions=['extra', 'codehilite', 'fenced_code', 'nl2br', 'tables', 'toc']
            )

            html_completo = template.render(
                titulo=titulo,
                nome_base=nome_base,
                logo_base64=logo_base64,
                html_corpo=html_corpo,
                data_hoje=datetime.now().strftime("%d/%m/%Y"),
                voltar_link="../index.html",
                voltar_texto="← Voltar à Página Inicial"
            )

            with open(caminho_html_destino, "w", encoding="utf-8") as f:
                f.write(html_completo)

            relatorios.append({
                "titulo": titulo,
                "link": f"reports/{arquivo_html_nome}"
            })

    relatorios.sort(key=lambda x: x["titulo"].lower())
    return relatorios


def processar_paginas():
    """
    Lê os arquivos Markdown da pasta 'content/pages', processa includes,
    converte para HTML e salva o resultado na pasta 'docs/pages'.
    Não retorna lista e nem gera índice global.
    """
    if not os.path.exists(PAGES_DIR):
        return

    destino_dir = os.path.join(OUTPUT_DOCS, "pages")
    os.makedirs(destino_dir, exist_ok=True)
    logo_base64 = carregar_logo_base64()
    template = jinja_env.get_template("report.html")

    for arquivo in os.listdir(PAGES_DIR):
        if arquivo.endswith(".md"):
            caminho_md = os.path.join(PAGES_DIR, arquivo)
            nome_base = os.path.splitext(arquivo)[0]
            arquivo_html_nome = f"{nome_base}.html"
            caminho_html_destino = os.path.join(destino_dir, arquivo_html_nome)

            with open(caminho_md, "r", encoding="utf-8") as f:
                conteudo_md = f.read()

            titulo = extrair_titulo_md(conteudo_md, nome_base)
            conteudo_md_limpo = re.sub(r"^---\s*\ntitle:.*?\n---\s*\n", "", conteudo_md, flags=re.MULTILINE | re.DOTALL)

            if "[TOC]" not in conteudo_md_limpo and "[toc]" not in conteudo_md_limpo:
                conteudo_md_limpo = f"[TOC]\n\n" + conteudo_md_limpo

            conteudo_md_processado = resolver_includes_assets(conteudo_md_limpo)

            html_corpo = markdown.markdown(
                conteudo_md_processado,
                extensions=['extra', 'codehilite', 'fenced_code', 'nl2br', 'tables', 'toc']
            )

            html_completo = template.render(
                titulo=titulo,
                nome_base=nome_base,
                logo_base64=logo_base64,
                html_corpo=html_corpo,
                data_hoje=datetime.now().strftime("%d/%m/%Y"),
                voltar_link="../index.html",
                voltar_texto="← Voltar à Página Inicial"
            )

            with open(caminho_html_destino, "w", encoding="utf-8") as f:
                f.write(html_completo)


def processar_tutoriais():
    """Lê a pasta tutoriais, processa includes, converte para HTML e gera lista alfabética."""
    if not os.path.exists(TUTORIAIS_DIR):
        return []

    os.makedirs(OUTPUT_TUTORIAIS, exist_ok=True)
    tutoriais = []
    template = jinja_env.get_template("tutorial.html")

    for arquivo in sorted(os.listdir(TUTORIAIS_DIR)):
        if arquivo.endswith(".md"):
            caminho_md = os.path.join(TUTORIAIS_DIR, arquivo)
            nome_base = os.path.splitext(arquivo)[0]
            arquivo_html_nome = f"{nome_base}.html"
            caminho_html_destino = os.path.join(OUTPUT_TUTORIAIS, arquivo_html_nome)

            with open(caminho_md, "r", encoding="utf-8") as f:
                conteudo_md = f.read()

            titulo = extrair_titulo_md(conteudo_md, nome_base)
            conteudo_md_limpo = re.sub(r"^---\s*\ntitle:.*?\n---\s*\n", "", conteudo_md, flags=re.MULTILINE | re.DOTALL)

            if "[TOC]" not in conteudo_md_limpo and "[toc]" not in conteudo_md_limpo:
                conteudo_md_limpo = f"[TOC]\n\n" + conteudo_md_limpo

            conteudo_md_processado = resolver_includes_assets(conteudo_md_limpo)
            conteudo_md_processado = resolver_includes_html(conteudo_md_processado)

            html_corpo = markdown.markdown(
                conteudo_md_processado,
                extensions=['extra', 'codehilite', 'fenced_code', 'nl2br', 'tables', 'toc']
            )

            html_completo = template.render(
                titulo=titulo,
                html_corpo=html_corpo,
                voltar_link="../index.html",
                voltar_texto="← Voltar à Página Inicial"
            )

            with open(caminho_html_destino, "w", encoding="utf-8") as f:
                f.write(html_completo)

            tutoriais.append({
                "titulo": titulo,
                "link": f"tutorial/{arquivo_html_nome}"
            })

    tutoriais.sort(key=lambda x: x["titulo"].lower())
    return tutoriais


def load_siglas():
    siglas = {}
    path = os.path.join("content", "siglas.csv")

    if not os.path.exists(path):
        return siglas

    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            siglas[row["sigla"]] = row["significado"]

    return siglas


def converter_md_para_html(codigo_task):
    origem_md = os.path.join("content", "documentation", f"{codigo_task}.md")
    dir_destino = os.path.join(OUTPUT_DIR, "documentation")
    arquivo_destino = os.path.join(dir_destino, f"{codigo_task}.html")

    if not os.path.exists(origem_md):
        return False

    os.makedirs(dir_destino, exist_ok=True)
    template = jinja_env.get_template("documentation.html")

    try:
        with open(origem_md, "r", encoding="utf-8") as f:
            conteudo_md = f.read()

        if "[TOC]" not in conteudo_md and "[toc]" not in conteudo_md:
            conteudo_md = "[TOC]\n\n" + conteudo_md

        conteudo_md_processado = resolver_includes_assets(conteudo_md)
        conteudo_md_processado = resolver_includes_html(conteudo_md_processado)

        html_corpo = markdown.markdown(
            conteudo_md_processado,
            extensions=['extra', 'codehilite', 'fenced_code', 'nl2br', 'tables', 'toc']
        )

        caminho_task = os.path.join(TASKS_DIR, f"{codigo_task}.json")
        titulo_task = codigo_task
        if os.path.exists(caminho_task):
            with open(caminho_task, encoding="utf-8") as f:
                titulo_task = json.load(f).get("titulo") or codigo_task
        html_completo = template.render(
            codigo_task=codigo_task,
            titulo_task=titulo_task,
            html_corpo=html_corpo
        )

        with open(arquivo_destino, "w", encoding="utf-8") as f:
            f.write(html_completo)

        return True
    except Exception as e:
        print(f"Erro ao converter documentação {codigo_task}.md: {e}")
        return False


def load_tasks():
    tasks = []
    if not os.path.exists(TASKS_DIR):
        return tasks
    for file in os.listdir(TASKS_DIR):
        if file.endswith(".json"):
            path = os.path.join(TASKS_DIR, file)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

                if data.get("status") is not True:
                    continue

                data["codigo"] = file.replace(".json", "")
                tasks.append(data)
    return tasks


def load_issues(tasks):
    issues = []
    if not os.path.exists(ISSUES_DIR):
        return issues

    valid_tasks = {t["codigo"] for t in tasks}

    for file in os.listdir(ISSUES_DIR):
        if file.endswith(".json"):
            path = os.path.join(ISSUES_DIR, file)
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

                codigo = file.replace(".json", "")
                task_codigo = codigo.split("-")[0]

                if task_codigo not in valid_tasks:
                    continue

                data["codigo"] = codigo
                issues.append(data)

    return issues


def group_by_prefix(tasks):
    groups = defaultdict(list)
    for task in tasks:
        match = re.match(r"([a-zA-Z]+)", task["codigo"])
        prefix = match.group(1) if match else "outros"
        groups[prefix].append(task)
    return groups


def sort_tasks(tasks):
    return sorted(
        tasks,
        key=lambda t: int(re.search(r"\d+", t["codigo"]).group())
    )


def count_open_issues(task_codigo, issues):
    return len([
        i for i in issues
        if i["codigo"].startswith(task_codigo)
        and i.get("status") is True
    ])


# ----------------------------------------------------------------------
# Reuniões (página docs/reunioes.html) — content/meetings/AAAA-MM-DD-<titulo>.json
# ----------------------------------------------------------------------
DIAS_CURTOS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def nome_curto(nome):
    """'Pedro Luis Borges de Souza Filho' → 'Pedro Souza Filho'; 'Mônica Colacique' → igual."""
    partes = nome.split()
    if len(partes) <= 2:
        return nome
    if partes[-1].lower() in ("filho", "júnior", "junior", "neto", "sobrinho") and len(partes) >= 3:
        return f"{partes[0]} {partes[-2]} {partes[-1]}"
    return f"{partes[0]} {partes[-1]}"


def preparar_reunioes(all_issues):
    hoje = datetime.now().date()
    por_codigo = {i["codigo"]: i for i in all_issues}
    reunioes = []
    if os.path.isdir(MEETINGS_DIR):
        for arquivo in sorted(os.listdir(MEETINGS_DIR)):
            if not arquivo.endswith(".json"):
                continue
            with open(os.path.join(MEETINGS_DIR, arquivo), encoding="utf-8") as f:
                r = json.load(f)
            try:
                data = datetime.strptime(r.get("data", ""), "%Y-%m-%d").date()
            except ValueError:
                print(f"⚠ {arquivo}: data inválida — ignorada.")
                continue
            pautas = []
            for cod in r.get("issues", []):
                i = por_codigo.get(cod)
                pautas.append({
                    "codigo": cod, "numero": i["numero"] if i else None,
                    "task_codigo": cod.rsplit("-", 1)[0], "existe": bool(i),
                    "titulo_task": i["titulo_task"] if i else "",
                    "descricao": i["descricao"] if i else "(issue não encontrada)",
                    "responsavel": (i["responsavel"] if i else "") or "sem responsável",
                    "resolvida": bool(i) and not i["aberta"],
                    "data_fechamento": i["data_fechamento"] if i else "",
                })
            reunioes.append({
                "arquivo": arquivo, "id": id_reuniao(arquivo),
                "titulo": r.get("titulo", ""), "data": data,
                "data_br": f"{DIAS_CURTOS[data.weekday()]} {data.strftime('%d/%m/%Y')}",
                "horario": r.get("horario", ""),
                "participantes": [{"nome": n, "curto": nome_curto(n)} for n in r.get("participantes", [])],
                "pautas": pautas,
                "texto": r.get("texto", ""),
                "email_enviado_em": r.get("email_enviado_em", ""),
                "cancelada_em": r.get("cancelada_em", ""),
                "motivo_cancelamento": r.get("motivo_cancelamento", ""),
                "futura": data >= hoje,
                "dias_ate": (data - hoje).days,
            })
    proximas = sorted([r for r in reunioes if r["futura"]], key=lambda r: (r["data"], r["horario"]))
    realizadas = sorted([r for r in reunioes if not r["futura"]], key=lambda r: (r["data"], r["horario"]), reverse=True)
    return proximas, realizadas


def dados_form_reuniao(all_issues):
    """Pessoas ativas e issues abertas para o formulário "+ Nova reunião" (renderizado no navegador)."""
    pessoas = [{"nome": p["nome"], "vinculo": p.get("vinculo", "")}
               for p in load_pessoas().values() if p["ativo"]]
    pessoas.sort(key=lambda p: (p["vinculo"] != "servidor", p["nome"]))
    issues = [{"codigo": i["codigo"], "numero": i["numero"], "tarefa": i["task_codigo"], "titulo_task": i["titulo_task"],
               "descricao": i["descricao"],
               "responsavel": "" if i["responsavel"] in NAO_PESSOAS else i["responsavel"]}
              for i in all_issues if i["aberta"] and i["task_ativa"]]
    emails = {p["nome"]: True for p in load_pessoas().values() if p.get("email")}
    return {"hoje": datetime.now().date().isoformat(), "site": SITE_URL,
            "pessoas": pessoas, "issues": issues, "emails": emails}


def gerar_pagina_reunioes(all_issues):
    proximas, realizadas = preparar_reunioes(all_issues)
    dados_json = json.dumps(dados_form_reuniao(all_issues), ensure_ascii=False).replace("</", "<\\/")
    html = jinja_env.get_template("reunioes.html").render(
        proximas=proximas, realizadas=realizadas, dados_json=dados_json,
        data_hoje=datetime.now().strftime("%d/%m/%Y"))
    with open(os.path.join(OUTPUT_DIR, "reunioes.html"), "w", encoding="utf-8") as f:
        f.write(html)


def preparar_responsavel_summary(tasks):
    responsaveis = defaultdict(list)

    for task in tasks:
        lista_resp = responsaveis_da_tarefa(task) or ["Não definido"]

        for resp in lista_resp:
            responsaveis[resp].append(task)

    nomes = sorted(responsaveis.keys(), key=lambda x: (x == "Desativado", x))
    summary = []

    for nome in nomes:
        tarefas = responsaveis[nome]
        total_peso = sum(t.get("peso", 0) for t in tarefas)
        safe_id = re.sub(r"\s+", "_", nome.lower())

        tarefas_ordenadas = sorted(tarefas, key=lambda x: x["codigo"])
        summary.append({
            "nome": nome,
            "safe_id": safe_id,
            "total_peso": total_peso,
            "tarefas": [
                {
                    "codigo": t["codigo"],
                    "titulo": t.get("titulo", ""),
                    "peso": t.get("peso", "")
                }
                for t in tarefas_ordenadas
            ]
        })

    return summary


def preparar_estagiario_summary(tasks):
    estagiarios = defaultdict(list)

    for task in tasks:
        # estagiários marcados como inativos na tarefa não aparecem no site
        for est in estagiarios_da_tarefa(task):
            estagiarios[est].append(task)

    nomes = sorted(estagiarios.keys())
    summary = []

    for nome in nomes:
        tarefas = estagiarios[nome]
        total_peso = sum(t.get("peso", 0) for t in tarefas)

        tarefas_ordenadas = sorted(tarefas, key=lambda x: x["codigo"])
        summary.append({
            "nome": nome,
            "safe_id": re.sub(r"\s+", "_", nome.lower()),
            "total_peso": total_peso,
            "tarefas": [
                {
                    "codigo": t["codigo"],
                    "titulo": t.get("titulo", ""),
                    "peso": t.get("peso", "")
                }
                for t in tarefas_ordenadas
            ]
        })

    return summary


def preparar_grupos_tarefas(tasks, issues):
    siglas = load_siglas()
    groups = group_by_prefix(tasks)
    sorted_prefixes = sorted(groups.keys())

    grupos_tarefas = []
    for prefix in sorted_prefixes:
        tasks_ordenadas = sort_tasks(groups[prefix])
        tasks_formatadas = []

        for task in tasks_ordenadas:
            descricao = task.get("descricao", "")
            if descricao.endswith(".tex"):
                path_tex = os.path.join(TASKS_DIR, f"{task['codigo']}.tex")
                if os.path.exists(path_tex):
                    descricao = Path(path_tex).read_text(encoding="utf-8")

            related = [
                i for i in issues
                if i["codigo"].startswith(task["codigo"])
                and i.get("status") is True
            ]

            badge = f"{len(related)} pendência(s)" if related else ""
            tem_documentacao = converter_md_para_html(task["codigo"])

            pendencias_formatadas = [
                {
                    "codigo": issue.get("codigo"),
                    "numero": issue.get("numero"),
                    "descricao_html": latex_to_html(issue.get("descricao", "")),
                    "responsavel": issue.get("responsavel") or "",
                    "comentarios": issue.get("comentarios", []),
                }
                for issue in sorted(related, key=lambda i: i.get("numero") or 0)
            ]

            responsaveis_str = "; ".join(responsaveis_da_tarefa(task))
            estagiarios_str = "; ".join(estagiarios_da_tarefa(task))

            tasks_formatadas.append({
                "codigo": task["codigo"],
                "titulo": task.get("titulo", ""),
                "peso": task.get("peso", ""),
                "responsaveis_str": responsaveis_str,
                "estagiarios_str": estagiarios_str,
                "descricao_html": latex_to_html(descricao),
                "badge": badge,
                "tem_documentacao": tem_documentacao,
                "pendencias": pendencias_formatadas
            })

        grupos_tarefas.append({
            "prefix": prefix,
            "significado": siglas.get(prefix, ""),
            "tasks": tasks_formatadas
        })

    return grupos_tarefas


# ----------------------------------------------------------------------
# Dashboard e relatório de issues resolvidas
# ----------------------------------------------------------------------
NAO_PESSOAS = {"", "Vago", "Não definido", "Desativado"}
MESES_PT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def parse_data_br(valor):
    try:
        return datetime.strptime(str(valor).strip(), "%d/%m/%Y").date()
    except (TypeError, ValueError):
        return None


def load_all_tasks():
    """Todas as tarefas (ativas e inativas), por código."""
    tasks = {}
    if not os.path.exists(TASKS_DIR):
        return tasks
    for file in os.listdir(TASKS_DIR):
        if file.endswith(".json"):
            with open(os.path.join(TASKS_DIR, file), encoding="utf-8") as f:
                data = json.load(f)
            data["codigo"] = file.replace(".json", "")
            tasks[data["codigo"]] = data
    return tasks


def load_all_issues(all_tasks):
    """Todas as issues, enriquecidas com tarefa, datas e tempo de resolução."""
    siglas = load_siglas()
    issues = []
    if not os.path.exists(ISSUES_DIR):
        return issues
    for file in sorted(os.listdir(ISSUES_DIR)):
        if not file.endswith(".json"):
            continue
        with open(os.path.join(ISSUES_DIR, file), encoding="utf-8") as f:
            data = json.load(f)
        codigo = file.replace(".json", "")
        task_codigo = codigo.split("-")[0]
        task = all_tasks.get(task_codigo, {})
        prefixo = re.match(r"([a-zA-Z]+)", task_codigo).group(1)
        abertura = parse_data_br(data.get("data"))
        fechamento = parse_data_br(data.get("data_fechamento"))
        dias = (fechamento - abertura).days if abertura and fechamento else None
        issues.append({
            "codigo": codigo,
            "numero": data.get("numero"),
            "task_codigo": task_codigo,
            "task_ativa": task.get("status") is True,
            "titulo_task": task.get("titulo", "N/A"),
            "prefixo": prefixo,
            "area": siglas.get(prefixo, ""),
            "responsavel": (data.get("responsavel") or "").strip(),
            "descricao": data.get("descricao", ""),
            "aberta": data.get("status") is True,
            "data": data.get("data", ""),
            "data_fechamento": data.get("data_fechamento", ""),
            "abertura": abertura,
            "fechamento": fechamento,
            "dias": dias,
            "comentarios": data.get("comentarios", []),
        })
    return issues


def _media(valores):
    return round(sum(valores) / len(valores), 1) if valores else None


def _mediana(valores):
    if not valores:
        return None
    v = sorted(valores)
    meio = len(v) // 2
    return v[meio] if len(v) % 2 else round((v[meio - 1] + v[meio]) / 2, 1)


def preparar_dashboard(tasks, all_issues):
    hoje = datetime.now().date()
    pessoas = load_pessoas()
    abertas = [i for i in all_issues if i["aberta"] and i["task_ativa"]]
    resolvidas = [i for i in all_issues if not i["aberta"]]
    tempos = [i["dias"] for i in resolvidas if i["dias"] is not None]

    # ---- por pessoa ----
    stats = {}

    def pessoa(nome):
        if nome not in stats:
            p = pessoas.get(nome, {})
            stats[nome] = {
                "nome": nome,
                "vinculo": {"servidor": "Servidor(a)", "estagiario": "Estagiário(a)"}.get(p.get("vinculo"), "—"),
                "atividades": 0, "peso": 0, "atividades_estagio": 0,
                "abertas": 0, "resolvidas": 0, "tempos": [], "idades_abertas": [],
            }
        return stats[nome]

    for nome, p in pessoas.items():
        if p["ativo"]:
            pessoa(nome)
    for t in tasks:
        for r in responsaveis_da_tarefa(t):
            if r not in NAO_PESSOAS:
                s = pessoa(r)
                s["atividades"] += 1
                s["peso"] += t.get("peso", 0) or 0
        for e in estagiarios_da_tarefa(t):
            pessoa(e)["atividades_estagio"] += 1
    for i in abertas:
        if i["responsavel"] not in NAO_PESSOAS:
            s = pessoa(i["responsavel"])
            s["abertas"] += 1
            if i["abertura"]:
                s["idades_abertas"].append((hoje - i["abertura"]).days)
    for i in resolvidas:
        if i["responsavel"] not in NAO_PESSOAS:
            s = pessoa(i["responsavel"])
            s["resolvidas"] += 1
            if i["dias"] is not None:
                s["tempos"].append(i["dias"])

    max_issues = max([s["abertas"] + s["resolvidas"] for s in stats.values()] + [1])
    por_pessoa = []
    for s in stats.values():
        total = s["abertas"] + s["resolvidas"]
        por_pessoa.append({
            **{k: v for k, v in s.items() if k not in ("tempos", "idades_abertas")},
            "total_issues": total,
            "taxa": round(100 * s["resolvidas"] / total) if total else None,
            "tempo_medio": _media(s["tempos"]),
            "tempo_mediano": _mediana(s["tempos"]),
            "n_tempos": len(s["tempos"]),
            "mais_antiga": max(s["idades_abertas"]) if s["idades_abertas"] else None,
            "pct_abertas": round(100 * s["abertas"] / max_issues, 1),
            "pct_resolvidas": round(100 * s["resolvidas"] / max_issues, 1),
            "safe_id": re.sub(r"\s+", "_", s["nome"].lower()),
        })
    por_pessoa.sort(key=lambda x: (-x["abertas"], -x["atividades"], x["nome"]))

    # ---- por mês (últimos 12) ----
    meses = []
    ano, mes = hoje.year, hoje.month
    for _ in range(12):
        meses.append((ano, mes))
        ano, mes = (ano, mes - 1) if mes > 1 else (ano - 1, 12)
    meses.reverse()
    por_mes = []
    for ano, mes in meses:
        criadas = sum(1 for i in all_issues if i["abertura"] and (i["abertura"].year, i["abertura"].month) == (ano, mes))
        fechadas = sum(1 for i in resolvidas if i["fechamento"] and (i["fechamento"].year, i["fechamento"].month) == (ano, mes))
        por_mes.append({"rotulo": f"{MESES_PT[mes - 1]}/{str(ano)[2:]}", "criadas": criadas, "resolvidas": fechadas})
    max_mes = max([max(m["criadas"], m["resolvidas"]) for m in por_mes] + [1])
    for m in por_mes:
        m["h_criadas"] = round(100 * m["criadas"] / max_mes, 1)
        m["h_resolvidas"] = round(100 * m["resolvidas"] / max_mes, 1)

    # ---- por área (sigla) ----
    siglas = load_siglas()
    areas = defaultdict(lambda: {"abertas": 0, "resolvidas": 0, "atividades": 0})
    for t in tasks:
        areas[re.match(r"([a-zA-Z]+)", t["codigo"]).group(1)]["atividades"] += 1
    for i in abertas:
        areas[i["prefixo"]]["abertas"] += 1
    for i in resolvidas:
        areas[i["prefixo"]]["resolvidas"] += 1
    max_area = max([a["abertas"] + a["resolvidas"] for a in areas.values()] + [1])
    por_area = sorted(
        [{"prefixo": k, "significado": siglas.get(k, ""), **v,
          "pct_abertas": round(100 * v["abertas"] / max_area, 1),
          "pct_resolvidas": round(100 * v["resolvidas"] / max_area, 1)}
         for k, v in areas.items() if v["atividades"] or v["abertas"] or v["resolvidas"]],
        key=lambda a: (-(a["abertas"] + a["resolvidas"]), a["prefixo"]))

    kpis = {
        "atividades": len(tasks),
        "abertas": len(abertas),
        "nao_atribuidas": sum(1 for i in abertas if i["responsavel"] in NAO_PESSOAS),
        "resolvidas": len(resolvidas),
        "tempo_medio": _media(tempos),
        "tempo_mediano": _mediana(tempos),
        "n_tempos": len(tempos),
        "resolvidas_30d": sum(1 for i in resolvidas if i["fechamento"] and (hoje - i["fechamento"]).days <= 30),
    }
    return {"kpis": kpis, "por_pessoa": por_pessoa, "por_mes": por_mes, "por_area": por_area}


def preparar_resolvidas(all_issues):
    resolvidas = [i for i in all_issues if not i["aberta"]]
    resolvidas.sort(key=lambda i: (i["fechamento"] is None, -(i["fechamento"].toordinal() if i["fechamento"] else 0), i["codigo"]))
    anos = sorted({i["fechamento"].year for i in resolvidas if i["fechamento"]}, reverse=True)
    pessoas = sorted({i["responsavel"] or "Não atribuído" for i in resolvidas})
    return resolvidas, anos, pessoas


def gerar_paginas_dashboard(tasks, all_issues):
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    dados = preparar_dashboard(tasks, all_issues)
    html = jinja_env.get_template("dashboard.html").render(data_hoje=data_hoje, **dados)
    with open(os.path.join(OUTPUT_DIR, "dashboard.html"), "w", encoding="utf-8") as f:
        f.write(html)

    resolvidas, anos, pessoas = preparar_resolvidas(all_issues)
    html = jinja_env.get_template("resolvidas.html").render(
        data_hoje=data_hoje, issues=resolvidas, anos=anos, pessoas=pessoas)
    with open(os.path.join(OUTPUT_DIR, "issues-resolvidas.html"), "w", encoding="utf-8") as f:
        f.write(html)


# ----------------------------------------------------------------------
# Acompanhamento (conversas 1:1 do gestor)
# ----------------------------------------------------------------------
FAIXAS_IDADE = [
    # (chave, rótulo, limite superior em dias)
    ("recente", "≤ 30 dias", 30),
    ("andamento", "31–90 dias", 90),
    ("atencao", "91–180 dias", 180),
    ("parada", "> 180 dias", None),
]


def slug(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-")


def faixa_idade(dias):
    if dias is None:
        return "sem_data"
    for chave, _, limite in FAIXAS_IDADE:
        if limite is None or dias <= limite:
            return chave
    return "parada"


def preparar_acompanhamento(tasks, all_issues):
    """
    Dados da página de acompanhamento. A página é renderizada no navegador (JS) a partir
    deste JSON, para que as mudanças feitas na reunião apareçam na hora.
    """
    hoje = datetime.now().date()
    pessoas = load_pessoas()

    abertas = [i for i in all_issues if i["aberta"] and i["task_ativa"]]
    resolvidas = [i for i in all_issues if not i["aberta"]]
    for i in abertas:
        i["idade"] = (hoje - i["abertura"]).days if i["abertura"] else None
        i["faixa"] = faixa_idade(i["idade"])

    atividades = defaultdict(list)
    for t in tasks:
        resp = responsaveis_da_tarefa(t)
        for r in resp:
            if r not in NAO_PESSOAS:
                atividades[r].append({"codigo": t["codigo"], "titulo": t.get("titulo", ""),
                                      "peso": t.get("peso", 0) or 0, "unico": len(resp) == 1,
                                      "papel": "responsável"})
        for e in estagiarios_da_tarefa(t):
            atividades[e].append({"codigo": t["codigo"], "titulo": t.get("titulo", ""),
                                  "peso": t.get("peso", 0) or 0, "unico": False,
                                  "papel": "estagiário(a)"})

    nomes = [n for n, p in pessoas.items() if p["ativo"]]
    for n in list(atividades) + [i["responsavel"] for i in abertas]:
        if n not in NAO_PESSOAS and n not in nomes:
            nomes.append(n)

    lista_pessoas = []
    for nome in nomes:
        p = pessoas.get(nome, {})
        ativs = sorted(atividades.get(nome, []), key=lambda a: a["codigo"])
        res90 = sorted(
            [i for i in resolvidas if i["responsavel"] == nome and i["fechamento"]
             and (hoje - i["fechamento"]).days <= 90],
            key=lambda i: i["fechamento"], reverse=True)
        lista_pessoas.append({
            "nome": nome,
            "id": slug(nome),
            "vinculo": p.get("vinculo", ""),
            "local": p.get("local", ""),
            "peso": sum(a["peso"] for a in ativs if a["papel"] == "responsável"),
            "unicas": sum(1 for a in ativs if a["unico"]),
            "resolvidas_total": sum(1 for i in resolvidas if i["responsavel"] == nome),
            "atividades": ativs,
            "resolvidas90": [{"codigo": i["codigo"], "numero": i["numero"], "descricao": i["descricao"],
                              "data_fechamento": i["data_fechamento"], "dias": i["dias"]} for i in res90],
        })
    lista_pessoas.sort(key=lambda x: x["nome"])

    pesos = [x["peso"] for x in lista_pessoas if x["vinculo"] == "servidor" and x["peso"]]
    media_peso = (sum(pesos) / len(pesos)) if pesos else 0

    # maior número de issue já usado em cada tarefa (abertas e fechadas), para prever códigos novos
    ultimo = {}
    for i in all_issues:
        tarefa, _, num = i["codigo"].rpartition("-")
        if num.isdigit():
            ultimo[tarefa] = max(ultimo.get(tarefa, 0), int(num))

    dados = {
        "hoje": hoje.isoformat(),
        "ultimo": ultimo,
        "media_peso": round(media_peso, 1),
        "pessoas": lista_pessoas,
        "tarefas": [{"codigo": t["codigo"], "titulo": t.get("titulo", ""),
                     "pessoas": [n for n in responsaveis_da_tarefa(t) + estagiarios_da_tarefa(t)
                                 if n not in NAO_PESSOAS]}
                    for t in sorted(tasks, key=lambda t: t["codigo"])],
        "issues": [{"codigo": i["codigo"], "numero": i["numero"], "tarefa": i["task_codigo"], "descricao": i["descricao"],
                    "responsavel": "" if i["responsavel"] in NAO_PESSOAS else i["responsavel"],
                    "data": i["data"], "idade": i["idade"], "comentarios": i["comentarios"]}
                   for i in sorted(abertas, key=lambda i: i["codigo"])],
    }

    # resumo para o cartão da home
    resumo_faixas = [{"chave": c, "rotulo": r, "total": sum(1 for i in abertas if i["faixa"] == c)}
                     for c, r, _ in FAIXAS_IDADE]
    return {
        "dados": dados,
        "total_abertas": len(abertas),
        "resumo_faixas": resumo_faixas,
        "nao_atribuidas": [i for i in abertas if i["responsavel"] in NAO_PESSOAS],
    }


def gerar_pagina_acompanhamento(tasks, all_issues):
    acomp = preparar_acompanhamento(tasks, all_issues)
    dados_json = json.dumps(acomp["dados"], ensure_ascii=False).replace("</", "<\\/")
    html = jinja_env.get_template("acompanhamento.html").render(
        data_hoje=datetime.now().strftime("%d/%m/%Y"), dados_json=dados_json)
    with open(os.path.join(OUTPUT_DIR, "acompanhamento.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return acomp


def _modulo_script(nome):
    """Importa um módulo de scripts/ (ex: dio, topologia)."""
    import importlib
    import sys
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
    if pasta not in sys.path:
        sys.path.insert(0, pasta)
    return importlib.import_module(nome)


def texto_puro(descricao, limite=420):
    """Descrição (LaTeX simplificado) → texto curto, para o tooltip do organograma."""
    html = latex_to_html(descricao or "")
    texto = re.sub(r"<li>", " • ", html)
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})?", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto if len(texto) <= limite else texto[: limite - 1].rstrip() + "…"


# Áreas do organograma (código usado na coluna "area" de content/siglas.csv): nome e cor.
AREAS = {
    "DE": ("Desenvolvimento", "lightpink"),
    "SE": ("Servidores", "honeydew"),
    "SU": ("Suporte", "lightblue"),
    "RE": ("Rede", "lavender"),
    "SI": ("Sites", "lightgray"),
    "AS": ("Administração de Sistemas", "#eedd82"),
    "GE": ("Gestão", "lightcoral"),
    "CC": ("Computação Científica", "aliceblue"),
    "PU": ("Projetos USP", "beige"),
}


def preparar_organograma(tasks, issues):
    """Árvore TI FFLCH → áreas → siglas → tarefas, para o organograma interativo da home."""
    areas = AREAS
    siglas_area = {}
    path = os.path.join("content", "siglas.csv")
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            siglas_area[row["sigla"]] = (row.get("area", ""), row["significado"])

    abertas = defaultdict(int)
    for i in issues:
        if i.get("status") is True:
            abertas[i["codigo"].split("-")[0]] += 1

    groups = group_by_prefix(tasks)
    filhos_area = defaultdict(list)
    for prefix in sorted(groups):
        area, significado = siglas_area.get(prefix, ("", ""))
        tarefas = []
        for t in sort_tasks(groups[prefix]):
            descricao = t.get("descricao", "")
            if descricao.endswith(".tex"):
                path_tex = os.path.join(TASKS_DIR, f"{t['codigo']}.tex")
                descricao = Path(path_tex).read_text(encoding="utf-8") if os.path.exists(path_tex) else ""
            tarefas.append({
                "tipo": "tarefa",
                "nome": t["codigo"],
                "titulo": t.get("titulo", ""),
                "responsaveis": responsaveis_da_tarefa(t),
                "estagiarios": estagiarios_da_tarefa(t),
                "peso": t.get("peso", ""),
                "pendencias": abertas.get(t["codigo"], 0),
                "descricao": texto_puro(descricao),
                "documentacao": os.path.exists(os.path.join("content", "documentation", f"{t['codigo']}.md")),
            })
        filhos_area[area].append({
            "tipo": "sigla", "nome": prefix, "titulo": significado,
            "pendencias": sum(x["pendencias"] for x in tarefas), "children": tarefas,
        })

    raiz = {"tipo": "raiz", "nome": "TI FFLCH", "children": []}
    for codigo, (nome, cor) in areas.items():
        if filhos_area.get(codigo):
            raiz["children"].append({"tipo": "area", "nome": nome, "codigo": codigo, "cor": cor,
                                     "children": filhos_area[codigo]})
    sem_area = [x for k, v in filhos_area.items() if k not in areas for x in v]
    if sem_area:
        raiz["children"].append({"tipo": "area", "nome": "Outros", "codigo": "", "cor": "lightyellow",
                                 "children": sem_area})
    return json.dumps(raiz, ensure_ascii=False).replace("</", "<\\/")


# ----------------------------------------------------------------------
# Página do GitHub (dados coletados por bin/claude_housekeeping_github.py)
# ----------------------------------------------------------------------
GITHUB_JSON = os.path.join("content", "github.json")
GITHUB_ORGS = ["fflch", "uspdev"]
GITHUB_SITUACOES = [("publico", "Público"), ("arquivado", "Arquivado"), ("privado", "Privado")]
GITHUB_SEM_TAREFA = {"fflch": "sem tarefa para este repositório", "uspdev": "projeto não usado na FFLCH"}


def _idade(dias):
    if dias is None:
        return "—"
    if dias < 1:
        return "hoje"
    if dias < 60:
        return f"{dias} dia{'s' if dias > 1 else ''}"
    if dias < 730:
        return f"{dias // 30} meses"
    return f"{dias // 365} anos"


def gerar_pagina_github():
    """docs/github.html a partir de content/github.json (o JSON é gerado localmente e versionado)."""
    if not os.path.exists(GITHUB_JSON):
        print("ℹ content/github.json não existe; página do GitHub não gerada.")
        return
    with open(GITHUB_JSON, encoding="utf-8") as f:
        dados = json.load(f)

    agora = datetime.now().astimezone()
    rotulos = dict(GITHUB_SITUACOES)
    ordem_sit = {s: i for i, (s, _) in enumerate(GITHUB_SITUACOES)}
    ordem_org = {o: i for i, o in enumerate(GITHUB_ORGS)}

    repos = []
    for r in dados["repos"]:
        dias, data_commit = None, ""
        if r.get("ultimo_commit"):
            dt = datetime.fromisoformat(r["ultimo_commit"].replace("Z", "+00:00"))
            dias = max((agora - dt).days, 0)
            data_commit = dt.astimezone().strftime("%d/%m/%Y")
        responsaveis = list(dict.fromkeys(p for t in r["tarefas"] for p in t.get("responsaveis", [])))
        repos.append({
            **r,
            "dias": dias,
            "idade": _idade(dias),
            "ultimo_commit_data": data_commit,
            "responsaveis": responsaveis,
            "total_commits": sum(n for _, n in r.get("commiters", [])),
            "situacao_rotulo": rotulos.get(r["situacao"], r["situacao"]),
            "sem_tarefa_msg": GITHUB_SEM_TAREFA.get(r["org"], "sem tarefa"),
            "grupo": f"{r['org']} · {rotulos.get(r['situacao'], r['situacao'])}",
            "recencia": "" if dias is None else ("recente" if dias <= 90 else "medio" if dias <= 365 else "antigo"),
        })
    repos.sort(key=lambda r: (ordem_org.get(r["org"], 99), ordem_sit.get(r["situacao"], 99), r["nome"].lower()))
    por_grupo = defaultdict(int)
    for r in repos:
        por_grupo[r["grupo"]] += 1
    for r in repos:
        r["grupo_total"] = por_grupo[r["grupo"]]

    kpis = []
    for org in GITHUB_ORGS:
        rs = [r for r in repos if r["org"] == org]
        pub = [r for r in rs if r["situacao"] == "publico"]
        kpis.append({
            "org": org, "total": len(rs), "publicos": len(pub),
            "sem_tarefa": sum(1 for r in pub if not r["tarefas"]),
            "sem_tarefa_rotulo": "não usados na fflch" if org == "uspdev" else "sem tarefa",
            "arquivados": sum(1 for r in rs if r["situacao"] == "arquivado"),
            "privados": sum(1 for r in rs if r["situacao"] == "privado"),
        })

    gerado = datetime.fromisoformat(dados["gerado_em"]).strftime("%d/%m/%Y %H:%M")
    html = jinja_env.get_template("github.html").render(repos=repos, kpis=kpis, gerado_em=gerado)
    with open(os.path.join(OUTPUT_DIR, "github.html"), "w", encoding="utf-8") as f:
        f.write(html)


def generate_html(tasks, issues, tutoriais, relatorios, acomp):
    siglas = load_siglas()
    responsaveis_summary = preparar_responsavel_summary(tasks)
    estagiarios_summary = preparar_estagiario_summary(tasks)
    grupos_tarefas = preparar_grupos_tarefas(tasks, issues)

    template = jinja_env.get_template("index.html")
    return template.render(
        tutoriais=tutoriais,
        relatorios=relatorios,
        acomp=acomp,
        responsaveis_summary=responsaveis_summary,
        estagiarios_summary=estagiarios_summary,
        grupos_tarefas=grupos_tarefas,
        organograma_json=preparar_organograma(tasks, issues),
    )


def gerar_figuras():
    """
    Figuras e tabelas derivadas dos dados (antes ficavam em passos separados do deploy):
    - scripts/dio.py       → docs/dio.html (diagrama interativo de DIOs a partir de content/dio.csv, incluído na documentação pas007)
    - scripts/topologia.py → docs/topologia.png e docs/vlans.html (incluído na documentação rat003)
    """
    for nome in ("dio", "topologia"):
        _modulo_script(nome).main()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    gerar_figuras()

    processar_paginas()
    copy_assets()

    tasks = load_tasks()
    issues = load_issues(tasks)
    relatorios = processar_relatorios()
    tutoriais = processar_tutoriais()

    all_tasks = load_all_tasks()
    all_issues = load_all_issues(all_tasks)
    gerar_pagina_reunioes(all_issues)
    gerar_paginas_dashboard(tasks, all_issues)
    acomp = gerar_pagina_acompanhamento(tasks, all_issues)
    gerar_pagina_github()

    html = generate_html(tasks, issues, tutoriais, relatorios, acomp)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("Site e tutoriais gerados com sucesso em:", OUTPUT_DIR)


if __name__ == "__main__":
    main()