import os
import json
import re
from collections import defaultdict
from datetime import datetime
import shutil
import csv
from pathlib import Path
import markdown

OUTPUT_DIR = "docs"
TASKS_DIR = "tasks"
ISSUES_DIR = os.path.join(TASKS_DIR, "issues")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")
TUTORIAIS_DIR = "tutoriais"
ASSETS_DIR = "assets"
OUTPUT_TUTORIAIS = os.path.join(OUTPUT_DIR, "tutorial")
REPORTS_DIR = os.path.join("content", "reports")
OUTPUT_REPORTS = os.path.join(OUTPUT_DIR, "reports")

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

def copy_assets():
    destino = os.path.join(OUTPUT_DIR, "assets")

    if os.path.exists(destino):
        shutil.rmtree(destino)

    if os.path.exists(ASSETS_DIR):
        shutil.copytree(ASSETS_DIR, destino)

def extrai_participantes_csv(caminho_csv):
    nomes = []
    if not os.path.exists(caminho_csv):
        return ""
    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # Ignora linhas vazias
                nomes.append(row[0].strip())
    return ", ".join(nomes)

def processar_relatorios():
    """Lê a pasta content/reports, processa includes, converte para HTML e gera lista alfabética."""
    if not os.path.exists(REPORTS_DIR):
        return []

    os.makedirs(OUTPUT_REPORTS, exist_ok=True)
    relatorios = []

    css_style = """
        body { padding: 40px; background: #f8f9fa; } 
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        pre { border-radius: 6px; }
        .toc { 
            background: #f1f3f5; 
            padding: 15px 20px; 
            border-radius: 6px; 
            border-left: 4px solid #0d6efd; 
            margin-bottom: 30px; 
        }
        .toc ul { margin-bottom: 0; padding-left: 20px; }
        .toc a { text-decoration: none; color: #0d6efd; font-weight: 500; }
        .toc a:hover { text-decoration: underline; }
    """

    for arquivo in sorted(os.listdir(REPORTS_DIR)):
        if arquivo.endswith(".md"):
            caminho_md = os.path.join(REPORTS_DIR, arquivo)
            nome_base = os.path.splitext(arquivo)[0]
            arquivo_html_nome = f"{nome_base}.html"
            caminho_html_destino = os.path.join(OUTPUT_REPORTS, arquivo_html_nome)

            with open(caminho_md, "r", encoding="utf-8") as f:
                conteudo_md = f.read()

            titulo = extrair_titulo_md(conteudo_md, nome_base)
            
            # Remove Front Matter
            conteudo_md_limpo = re.sub(r"^---\s*\ntitle:.*?\n---\s*\n", "", conteudo_md, flags=re.MULTILINE | re.DOTALL)
            
            # Injeta TOC automático caso não exista
            if "[TOC]" not in conteudo_md_limpo and "[toc]" not in conteudo_md_limpo:
                conteudo_md_limpo = f"[TOC]\n\n" + conteudo_md_limpo

            # Processa includes de assets/
            conteudo_md_processado = resolver_includes_assets(conteudo_md_limpo)

            # Converte Markdown para HTML (tabelas, códigos, etc)
            html_corpo = markdown.markdown(
                conteudo_md_processado,
                extensions=['extra', 'codehilite', 'fenced_code', 'nl2br', 'tables', 'toc']
            )

            # Template HTML individual do relatório (com suporte ao MathJax para fórmulas matemáticas)
            html_completo = f"""<!DOCTYPE html>
                <html lang="pt-br">
                <head>
                    <meta charset="UTF-8">
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                    <!-- Prism CSS para realce de sintaxe -->
                    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
                    <!-- MathJax para renderização de fórmulas e equações LaTeX -->
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/polyfill/3.25.1/polyfill.min.js"></script>
                    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
                    <title>{titulo}</title>
                    <style>{css_style}</style>
                </head>
                <body>
                    <div class="container">
                        <a href="../index.html" class="btn btn-sm btn-outline-secondary mb-4">← Voltar à Página Inicial</a>
                        <h1>{titulo}</h1>
                        <hr>
                        <div class="markdown-body">
                            {html_corpo}
                        </div>
                    </div>
                    <!-- Prism JS -->
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
                </body>
                </html>"""

            with open(caminho_html_destino, "w", encoding="utf-8") as f:
                f.write(html_completo)

            relatorios.append({
                "titulo": titulo,
                "link": f"reports/{arquivo_html_nome}"
            })

    relatorios.sort(key=lambda x: x["titulo"].lower())
    return relatorios

# ----------------------------------------
# PROCESSAR TUTORIAIS
# ----------------------------------------
def extrair_titulo_md(conteudo_md, nome_arquivo_padrao):
    """Extrai o título do Front Matter (--- title: Titulo ---) ou do primeiro header H1 (# Titulo)."""
    match_yaml = re.search(r"^---\s*\ntitle:\s*(.*?)\n---", conteudo_md, re.MULTILINE | re.IGNORECASE)
    if match_yaml:
        return match_yaml.group(1).strip()
    
    match_h1 = re.search(r"^#\s+(.*)", conteudo_md, re.MULTILINE)
    if match_h1:
        return match_h1.group(1).strip()
    
    return nome_arquivo_padrao.replace("-", " ").replace("_", " ").title()


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
            
            # 1. Verifica se o nome exato do arquivo está no mapeamento especial (ex: Dockerfile)
            if nome_arquivo in FILENAME_TO_LANG:
                lang = FILENAME_TO_LANG[nome_arquivo]
            # 2. Verifica se a extensão está mapeada
            elif ext in EXT_TO_LANG:
                lang = EXT_TO_LANG[ext]
            # 3. Fallback: usa 'bash' se não conseguir identificar a linguagem
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

def processar_tutoriais():
    """Lê a pasta tutoriais, processa inclui, converte para HTML e gera lista alfabética."""
    if not os.path.exists(TUTORIAIS_DIR):
        return []

    os.makedirs(OUTPUT_TUTORIAIS, exist_ok=True)
    tutoriais = []

    css_style = """
        body { padding: 40px; background: #f8f9fa; } 
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        pre { border-radius: 6px; }
        /* Estilização elegante para o Sumário gerado automaticamente */
        .toc { 
            background: #f1f3f5; 
            padding: 15px 20px; 
            border-radius: 6px; 
            border-left: 4px solid #0d6efd; 
            margin-bottom: 30px; 
        }
        .toc ul { margin-bottom: 0; padding-left: 20px; }
        .toc a { text-decoration: none; color: #0d6efd; font-weight: 500; }
        .toc a:hover { text-decoration: underline; }
    """

    for arquivo in sorted(os.listdir(TUTORIAIS_DIR)):
        if arquivo.endswith(".md"):
            caminho_md = os.path.join(TUTORIAIS_DIR, arquivo)
            nome_base = os.path.splitext(arquivo)[0]
            arquivo_html_nome = f"{nome_base}.html"
            caminho_html_destino = os.path.join(OUTPUT_TUTORIAIS, arquivo_html_nome)

            with open(caminho_md, "r", encoding="utf-8") as f:
                conteudo_md = f.read()

            titulo = extrair_titulo_md(conteudo_md, nome_base)
            
            # Remove Front Matter antes de converter se existir
            conteudo_md_limpo = re.sub(r"^---\s*\ntitle:.*?\n---\s*\n", "", conteudo_md, flags=re.MULTILINE | re.DOTALL)
            
            # Se o usuário NÃO colocou [TOC] manualmente no markdown, inserimos automaticamente no topo
            if "[TOC]" not in conteudo_md_limpo and "[toc]" not in conteudo_md_limpo:
                conteudo_md_limpo = f"[TOC]\n\n" + conteudo_md_limpo

            # Processa includes de assets/
            conteudo_md_processado = resolver_includes_assets(conteudo_md_limpo)

            # Converte Markdown para HTML com suporte a TOC automático e IDs nos headers
            html_corpo = markdown.markdown(
                conteudo_md_processado,
                extensions=['extra', 'codehilite', 'fenced_code', 'nl2br', 'tables', 'toc']
            )

            # Template HTML individual do tutorial
            html_completo = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Prism CSS para realce de sintaxe colorido -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <title>{titulo}</title>
    <style>{css_style}</style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="btn btn-sm btn-outline-secondary mb-4">← Voltar à Página Inicial</a>
        <h1>{titulo}</h1>
        <hr>
        <div class="markdown-body">
            {html_corpo}
        </div>
    </div>
    <!-- Prism JS e Autoloader para linguagens -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
</body>
</html>"""

            with open(caminho_html_destino, "w", encoding="utf-8") as f:
                f.write(html_completo)

            tutoriais.append({
                "titulo": titulo,
                "link": f"tutorial/{arquivo_html_nome}"
            })

    # Ordena alfabeticamente pelo título
    tutoriais.sort(key=lambda x: x["titulo"].lower())
    return tutoriais

def generate_issues_cards(tasks, issues):
    siglas = load_siglas()

    grupos = defaultdict(list)
    nao_atribuidos = []

    for issue in issues:
        if issue.get("status") is not True:
            continue

        responsavel = issue.get("responsavel")
        codigo = issue["codigo"]
        task_codigo = codigo.split("-")[0]

        if not responsavel:
            nao_atribuidos.append((task_codigo, issue))
            continue

        prefixo = re.match(r"([a-zA-Z]+)", task_codigo).group(1)
        grupos[prefixo].append((task_codigo, issue))

    prefixos = sorted(grupos.keys())

    html = """
<h2 id="pendencias" class="mt-5 text-danger"><u>Issues pendentes</u></h2>

<div class="container-fluid">
<div class="row">
"""

    for prefixo in prefixos:
        grupos[prefixo].sort(key=lambda x: x[1].get("data", ""))

        html += f"""
            <div class="col-md-4 mb-4">
            <div class="card border-danger shadow h-100">
            <div class="card-header bg-danger text-white text-center fw-bold">
            {prefixo} - {siglas.get(prefixo, "")}
            </div>
            <div class="card-body">
            """

        for task_codigo, issue in grupos[prefixo]:
            task = next((t for t in tasks if t["codigo"] == task_codigo), None)
            titulo = task.get("titulo", "") if task else "N/A"

            responsavel = issue.get("responsavel", "")
            safe_id = re.sub(r"\s+", "_", responsavel.lower())

            responsaveis = task.get("responsaveis") if task else []
            responsaveis_tarefa = ", ".join(map(str, responsaveis))

            html += f"""
                <div class="card mb-3 border-secondary shadow-sm">
                <div class="card-body">

                <strong>Atividade:</strong> {issue["codigo"].split('-')[0]} - {titulo}

                <p class="mb-1"><strong>Responsáveis da atividade:</strong> {responsaveis_tarefa}</p>

                <strong>Código da issue:</strong> {re.sub(r'^[a-zA-Z]+', '', issue["codigo"])}

                <p class="mb-0">
                <strong>Issue atribuída para:</strong>
                <a href="#resp-{safe_id}" class="fw-bold text-decoration-none">
                {responsavel}
                </a>
                </p>

                <p class="mb-1"><strong>Descrição da issue:</strong><br>
                {issue.get("descricao","")}
                </p>

                <p class="mb-1"><strong>Data:</strong> {issue.get("data","")}</p>

                </div>
                </div>
                """

        html += """
            </div>
            </div>
            </div>
            """

    html += """
        </div>
        </div>
        """

    if nao_atribuidos:
        nao_atribuidos.sort(key=lambda x: x[1].get("data", ""))

        html += """
            <h3 id="nao-atribuidos" class="mt-5 text-secondary"><u>Issues não atribuídas</u></h3>

            <div class="container-fluid">
            <div class="row">
            """

        for task_codigo, issue in nao_atribuidos:
            task = next((t for t in tasks if t["codigo"] == task_codigo), None)
            titulo = task.get("titulo", "") if task else "N/A"

            responsaveis = task.get("responsaveis") if task else []
            responsaveis_tarefa = ", ".join(map(str, responsaveis))

            prefixo = re.match(r"([a-zA-Z]+)", task_codigo).group(1)

            html += f"""
                <div class="col-md-4 mb-4">
                <div class="card border-secondary shadow h-100">
                <div class="card-header bg-secondary text-white text-center fw-bold">
                {prefixo} - {siglas.get(prefixo, "")}
                </div>
                <div class="card-body">

                <strong>Atividade:</strong> {issue["codigo"].split('-')[0]} - {titulo}

                <p class="mb-1"><strong>Responsáveis da atividade:</strong> {responsaveis_tarefa}</p>

                <strong>Código da issue:</strong> {re.sub(r'^[a-zA-Z]+', '', issue["codigo"])}

                <p class="mb-1"><strong>Descrição da issue:</strong><br>
                {issue.get("descricao","")}
                </p>

                <p class="mb-1"><strong>Data:</strong> {issue.get("data","")}</p>

                </div>
                </div>
                </div>
                """

        html += """
            </div>
            </div>
            """

    return html

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

    css_doc = """
        body { padding: 40px; background: #f8f9fa; } 
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }

        /* Estilização elegante para o Sumário (TOC) */
        .toc { 
            background: #f1f3f5; 
            padding: 15px 20px; 
            border-radius: 6px; 
            border-left: 4px solid #0d6efd; 
            margin-bottom: 30px; 
        }
        .toc ul { margin-bottom: 0; padding-left: 20px; }
        .toc a { text-decoration: none; color: #0d6efd; font-weight: 500; }
        .toc a:hover { text-decoration: underline; }
    """

    try:
        with open(origem_md, "r", encoding="utf-8") as f:
            conteudo_md = f.read()

        # Injeta automaticamente a tag [TOC] no topo caso não esteja presente no markdown
        if "[TOC]" not in conteudo_md and "[toc]" not in conteudo_md:
            conteudo_md = "[TOC]\n\n" + conteudo_md

        # Processa includes de assets/ caso existam
        conteudo_md_processado = resolver_includes_assets(conteudo_md)

        # Converte Markdown para HTML incluindo a extensão 'toc'
        html_corpo = markdown.markdown(
            conteudo_md_processado, 
            extensions=['extra', 'codehilite', 'fenced_code', 'nl2br', 'tables', 'toc']
        )

        html_completo = f"""<!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
                <title>Documentação - {codigo_task}</title>
                <style>{css_doc}</style>
            </head>
            <body>
                <div class="container">
                    <a href="../index.html" class="btn btn-sm btn-outline-secondary mb-4">← Voltar ao Planejamento</a>
                    <div class="markdown-body">
                        {html_corpo}
                    </div>
                </div>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
            </body>
            </html>"""

        with open(arquivo_destino, "w", encoding="utf-8") as f:
            f.write(html_completo)
            
        return True
    except Exception as e:
        print(f"Erro ao converter documentação {codigo_task}.md: {e}")
        return False
    
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

def generate_estagiario_summary(tasks, issues):
    estagiarios = defaultdict(list)

    for task in tasks:
        lista_est = task.get("estagiarios", [])
        if isinstance(lista_est, str):
            lista_est = [lista_est]

        for est in lista_est:
            if not est or est == "Não Há":
                continue
            estagiarios[est].append(task)

    nomes = sorted(estagiarios.keys())
    html = ''

    for nome in nomes:
        tarefas = estagiarios[nome]
        total_peso = sum(t.get("peso", 0) for t in tarefas)

        html += f"""
            <h3 class="mt-4">{nome}</h3>
            <table class="table table-bordered table-sm">
            <thead>
            <tr>
            <th style="width:120px;">Código</th>
            <th>Título</th>
            <th style="width:80px;">Peso</th>
            </tr>
            </thead>
            <tbody>
            """
        for t in sorted(tarefas, key=lambda x: x["codigo"]):
            html += f"""
                <tr>
                <td><a href="#{t["codigo"]}">{t["codigo"]}</a></td>
                <td>{t.get("titulo","")}</td>
                <td>{t.get("peso","")}</td>
                </tr>
                """

        html += f"""
            <tr class="table-secondary fw-bold">
            <td colspan="2">Soma</td>
            <td>{total_peso}</td>
            </tr>
            </tbody>
            </table>
            """

    return html

import os
import json
from datetime import datetime

def buscar_proxima_reuniao_e_issues(tipo_reuniao, dicionario_siglas, tasks):
    meetings_dir = "meetings"
    if not os.path.exists(meetings_dir):
        return "Nenhuma reunião agendada", ""

    hoje = datetime.now().date()
    reunioes_validas = []

    for f in os.listdir(meetings_dir):
        if f.startswith(f"{tipo_reuniao}-") and f.endswith(".json"):
            data_str = f.replace(f"{tipo_reuniao}-", "").replace(".json", "")
            try:
                data_reuniao = datetime.strptime(data_str, "%Y-%m-%d").date()
                if data_reuniao >= hoje:
                    reunioes_validas.append((data_reuniao, f))
            except ValueError:
                pass

    if not reunioes_validas:
        return "Nenhuma reunião agendada", ""

    reunioes_validas.sort(key=lambda x: x[0])
    data_proxima, arquivo_proxima = reunioes_validas[0]
    data_formatada_br = data_proxima.strftime("%d/%m/%Y")
    
    html_issues = ""
    try:
        with open(os.path.join(meetings_dir, arquivo_proxima), 'r', encoding='utf-8') as file:
            dados_reuniao = json.load(file)
            lista_issues = dados_reuniao.get("issues", [])
            lista_extra = dados_reuniao.get("extra", [])  # <--- Lê a lista extra
            
            # Verifica se existe algum item (issue ou extra)
            if lista_issues or lista_extra:
                html_issues += "<ul style='padding-left: 20px; margin-top: 5px; font-size: 0.9em;'>"
                
                # 1. Processa as issues registradas em arquivo
                for iss_arq in lista_issues:
                    caminho_issue_real = os.path.join("tasks", "issues", iss_arq)
                    issue = {}
                    if os.path.exists(caminho_issue_real):
                        try:
                            with open(caminho_issue_real, encoding="utf-8") as f_issue:
                                issue = json.load(f_issue)
                        except:
                            pass

                    task_codigo = iss_arq.split("-")[0]
                    task_mae = next((t for t in tasks if t["codigo"] == task_codigo), None)
                    titulo_task = task_mae.get("titulo", "N/A") if task_mae else "N/A"
                    
                    html_issues += f"""<li>
                        <strong>{titulo_task}</strong> - {issue.get("descricao")}
                        ({issue.get("responsavel", "Não atribuído")})<br>
                    </li>"""
                
                # 2. Processa os itens extras (sem arquivo de issue)
                for item_extra in lista_extra:
                    html_issues += f"""<li>
                        {item_extra}
                    </li>"""

                html_issues += "</ul>"
            else:
                html_issues = "<br><span class='text-muted'>Nenhuma pauta associada.</span>"
    except:
        html_issues = "<br><span class='text-danger'>Erro ao carregar pautas.</span>"

    return data_formatada_br, html_issues
    
def generate_responsavel_summary(tasks, issues):
    responsaveis = defaultdict(list)

    for task in tasks:
        lista_resp = task.get("responsaveis")
        if not lista_resp:
            antigo = task.get("responsavel")
            lista_resp = [antigo] if antigo else ["Não definido"]

        if isinstance(lista_resp, str):
            lista_resp = [lista_resp]

        for resp in lista_resp:
            responsaveis[resp].append(task)

    nomes = sorted(responsaveis.keys(), key=lambda x: (x == "Desativado", x))
    html = ''

    for nome in nomes:
        tarefas = responsaveis[nome]
        total_peso = sum(t.get("peso", 0) for t in tarefas)
        safe_id = re.sub(r"\s+", "_", nome.lower())

        html += f"""
            <h3 class="mt-4" id="resp-{safe_id}">{nome}</h3>
            <table class="table table-bordered table-sm">
            <thead>
            <tr>
            <th style="width:120px;">Código</th>
            <th>Título</th>
            <th style="width:80px;">Peso</th>
            </tr>
            </thead>
            <tbody>
            """
        for t in sorted(tarefas, key=lambda x: x["codigo"]):
            html += f"""
                <tr>
                <td><a href="#{t["codigo"]}">{t["codigo"]}</a></td>
                <td>{t.get("titulo","")}</td>
                <td>{t.get("peso","")}</td>
                </tr>
                """

        html += f"""
            <tr class="table-secondary fw-bold">
            <td colspan="2">Soma</td>
            <td>{total_peso}</td>
            </tr>
            </tbody>
            </table>
            """

    return html

arquivos_json = [
    'meeting-ti.json',
    'meeting-drupal.json',
    'meeting-camada1.json',
    'meeting-camada2.json',
    'meeting-laravel.json',
]

def generate_html(tasks, issues, tutoriais, relatorios):
    siglas = load_siglas()
    groups = group_by_prefix(tasks)
    sorted_prefixes = sorted(groups.keys())

    css_index = """
        body { padding: 40px; }
        .card { margin-bottom: 20px; }
        .prefix-title { margin-top: 80px; border-bottom: 2px solid #ddd; padding-bottom: 10px; }
        .issue-item { font-size: 0.9rem; color: #555; margin-left:15px; }
        .top-link { font-size: 0.85rem; }
        .summary-box { background:#f8f9fa; padding:20px; border-radius:10px; margin-bottom:40px; }
    """

    html = f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
        <meta charset="UTF-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>{css_index}</style>
        </head>
        <body>
        <div class="container-fluid">

        <a href="#top" class="top-link">(voltar ao topo)</a>
        <div class="mb-4">
        <h2>Sumário</h2>
        <ul>
            <li><a href="#tutoriais">Tutoriais</a></li>
            <li><a href="#pendencias">Issues pendentes</a></li>
            <li><a href="#nao-atribuidos">Issues não atribuídas</a></li>
            <li><a href="#por-pessoa">Atividades por funcionário(a)</a></li>
            <li><a href="#por-estagiario">Atividades por estagiário(a)</a></li>
            <li><a href="#estrutura">Organização estrutural das atividades</a></li>
            <li><a href="#reunioes">Reuniões Técnicas</a></li>
            <li><a href="#relatorios">Relatórios</a></li>
            
        </ul>
        </div>
        <div class="mb-5">
        <p>
        A organização das demandas da TI-FFLCH está estruturada de forma hierárquica.
        As atividades são agrupadas por áreas, como por exemplo <strong>Desenvolvimento (dev)</strong>.
        Dentro de cada área existem atividades específicas, identificadas por códigos como <strong>dev010</strong>,
        que representam uma unidade de trabalho, no caso, desenvolvimento do sistema de fechadura eletrônica. Por fim, cada atividade pode ter associada uma ou mais <strong>issues</strong>, que são tarefas menores ou pendências relacionadas àquela atividade, como por exemplo a implementação de um novo recurso no sistema de fechadura eletrônica, que teria código <strong>dev010-01</strong>.
        <br><br>
        Cada atividade pode possuir múltiplos responsáveis, enquanto as <strong>issues</strong> representam tarefas menores
        ou pendências associadas a uma atividade e são atribuídas a apenas uma pessoa.
        <br><br>
        A estrutura geral segue o modelo:
        <strong>Área → Atividade → Issue</strong>
        </p>
        </div>
        """
        
    html += """
        </div>

        <h1 id="reunioes">Reuniões Técnicas</h1>

        <p>
            As reuniões técnicas têm três objetivos principais. O primeiro é funcionar como um espaço formativo, no qual dedicamos de 15 a 30 minutos iniciais para que membros da equipe apresentem tutoriais ou realizem demonstrações práticas (labs). Esse momento será rotativo, garantindo a participação de todos e apoio da equipe.
            <br><br>
            O segundo momento é voltado à discussão dos problemas que precisam ser resolvidos, e por fim, a reunião se encerra com a definição e o encaminhamento das tarefas entre os membros da equipe.
        </p>

        <div class="row">
    """

    for arquivo in arquivos_json:
        caminho_json = f'content/{arquivo}'
        
        if os.path.exists(caminho_json):
            with open(caminho_json, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            titulo = dados.get('título', '')
            tipo_limpo = arquivo.replace('meeting-', '').replace('.json', '')
            
            nome_base_csv = arquivo.replace('.json', '.csv')
            string_participantes = extrai_participantes_csv(f'content/{nome_base_csv}')
            
            hands_on_html = ""
            if dados.get('handons'):
                hands_on_html = f"<p><strong>Hands-on:</strong><br>{dados['handons']}</p>"
                
            data_reuniao_texto, pautas_html = buscar_proxima_reuniao_e_issues(tipo_limpo, siglas, tasks)
            
            bloco_proxima_reuniao = f"<p><strong>Próxima Reunião:</strong><br>{data_reuniao_texto}</p>"
            if pautas_html:
                bloco_proxima_reuniao += f"<p><strong>Pautas / Issues da Reunião:</strong>{pautas_html}</p>"

            html += f"""
                <div class="col-md-4 mb-4">
                    <div class="card shadow h-100 border-success">
                        <div class="card-header bg-success text-white fw-bold text-center">
                            {titulo}
                        </div>
                        <div class="card-body">

                            <p><strong>Dia e horário:</strong><br>
                            {dados['Dia da semana']}<br>{dados['horário']}</p>

                            <p><strong>Participantes:</strong><br>
                            {string_participantes}</p>

                            {hands_on_html}
                            
                            <hr>
                            {bloco_proxima_reuniao}
                        </div>
                    </div>
                </div>
            """

    html += "\n</div>"

    # --- NOVA SEÇÃO DE TUTORIAIS EM ORDEM ALFABÉTICA ---
    html += """
    <hr class="my-5">
    <h1 id="tutoriais">Tutoriais Técnicos</h1>
    <div class="card shadow-sm mb-5">
        <div class="card-body">
            <ul class="list-group list-group-flush">
    """
    if tutoriais:
        for tut in tutoriais:
            html += f"""
                <li class="list-group-item">
                    <a href="{tut['link']}" class="fw-bold text-primary text-decoration-none" target="_blank">
                        📄 {tut['titulo']}
                    </a>
                </li>
            """
    else:
        html += '<li class="list-group-item text-muted">Nenhum tutorial cadastrado até o momento.</li>'

    html += """
            </ul>
        </div>
    </div>
    """

    html += generate_issues_cards(tasks, issues)
    html += '<h1 id="por-pessoa">Organização das atividades por pessoa</h1>'
    html += generate_responsavel_summary(tasks, issues)
    html += "<br><hr><h2 id='por-estagiario'><u>Estagiários(as)</u></h2>"
    html += generate_estagiario_summary(tasks, issues)

    html += '<div id="estrutura" class="summary-box">'
    html += """
        <h1>Organização estrutural das atividades</h1>
        <div class="mb-5">
        <img src="ti_fflch.jpg" class="img-fluid w-100" alt="TI FFLCH">
        </div>
        """
    html += '<ul>'

    for prefix in sorted_prefixes:
        significado = siglas.get(prefix, "")
        label = f"{prefix} - {significado}" if significado else prefix
        html += f'<li><a href="#{prefix}">{label}</a></li>'

    html += '</ul></div>'

    for prefix in sorted_prefixes:
        html += f'<h2 class="prefix-title" id="{prefix}">{prefix} '
        html += f'<a href="#top" class="top-link">(voltar ao topo)</a>'
        html += '</h2>'

        for task in sort_tasks(groups[prefix]):
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

            badge = f' <span class="badge bg-danger">{len(related)} pendência(s)</span>' if related else ""

            tem_documentacao = converter_md_para_html(task["codigo"])
            if tem_documentacao:
                link_doc = f" | <a href='documentation/{task['codigo']}.html' class='text-decoration-none fw-bold text-success' target='_blank'>Documentação</a>"
            else:
                link_doc = ""

            html += f"""
                <div class="card shadow-sm">
                <div class="card-body">
                <h5 id="{task["codigo"]}">{task["codigo"]} | {task["titulo"]}{link_doc} {badge}</h5>

                <table class="table table-sm">
                <tr><th style="width:120px;">Peso</th><td>{task.get("peso","")}</td></tr>
                <tr><th>Responsável(is)</th><td>{"; ".join(task.get("responsaveis", [task.get("responsavel","")]))}</td></tr>
                <tr><th>Estagiário(a)</th><td>{"; ".join(task.get("estagiarios", []))}</td></tr>
                </table>

                <div class="mt-3">
                {latex_to_html(descricao)}
                </div>
                """

            if related:
                html += "<hr><strong>Pendências:</strong>"
                for issue in related:
                    html += f"""
                        <div class="issue-item">
                        <strong>{issue.get("codigo")}</strong><br>
                        {latex_to_html(issue.get("descricao",""))}
                        </div>
                        """

            html += "</div></div>"

    # --- SEÇÃO DE RELATÓRIOS ---
    html += """
    <hr class="my-5">
    <h1 id="relatorios">Relatórios</h1>
    <div class="card shadow-sm mb-5">
        <div class="card-body">
            <ul class="list-group list-group-flush">
    """
    if relatorios:
        for rel in relatorios:
            html += f"""
                <li class="list-group-item">
                    <a href="{rel['link']}" class="fw-bold text-primary text-decoration-none" target="_blank">
                        📊 {rel['titulo']}
                    </a>
                </li>
            """
    else:
        html += '<li class="list-group-item text-muted">Nenhum relatório cadastrado até o momento.</li>'

    html += """
            </ul>
        </div>
    </div>
    """

    return html

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    copy_assets()

    tasks = load_tasks()
    issues = load_issues(tasks)
    relatorios = processar_relatorios()
    
    # Processa os tutoriais da pasta tutoriais/
    tutoriais = processar_tutoriais()

    html = generate_html(tasks, issues, tutoriais, relatorios)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("Site e tutoriais gerados com sucesso em:", OUTPUT_DIR)

if __name__ == "__main__":
    main()