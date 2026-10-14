import os
import json
import re
from collections import defaultdict
from datetime import datetime
import shutil
import csv
from pathlib import Path
import markdown
import base64
from jinja2 import Environment, FileSystemLoader

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


def extrai_participantes_csv(caminho_csv):
    nomes = []
    if not os.path.exists(caminho_csv):
        return ""
    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                nomes.append(row[0].strip())
    return ", ".join(nomes)


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

        html_completo = template.render(
            codigo_task=codigo_task,
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


def buscar_proxima_reuniao_e_issues(tipo_reuniao, dicionario_siglas, tasks):
    meetings_dir = MEETINGS_DIR
    if not os.path.exists(meetings_dir):
        return "Nenhuma reunião agendada", {"pautas": [], "erro": False}

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
        return "Nenhuma reunião agendada", {"pautas": [], "erro": False}

    reunioes_validas.sort(key=lambda x: x[0])
    data_proxima, arquivo_proxima = reunioes_validas[0]
    data_formatada_br = data_proxima.strftime("%d/%m/%Y")

    pautas = []
    try:
        with open(os.path.join(meetings_dir, arquivo_proxima), 'r', encoding='utf-8') as file:
            dados_reuniao = json.load(file)
            lista_issues = dados_reuniao.get("issues", [])
            lista_extra = dados_reuniao.get("extra", [])

            for iss_arq in lista_issues:
                caminho_issue_real = os.path.join(ISSUES_DIR, iss_arq)
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

                pautas.append({
                    "tipo": "issue",
                    "titulo_task": titulo_task,
                    "descricao": issue.get("descricao", ""),
                    "responsavel": issue.get("responsavel", "Não atribuído")
                })

            for item_extra in lista_extra:
                pautas.append({
                    "tipo": "extra",
                    "texto": item_extra
                })

        return data_formatada_br, {"pautas": pautas, "erro": False}
    except:
        return data_formatada_br, {"pautas": [], "erro": True}


def obter_dados_reunioes(siglas, tasks):
    arquivos_json = [
        'meeting-ti.json',
        'meeting-drupal.json',
        'meeting-camada1.json',
        'meeting-camada2.json',
        'meeting-laravel.json',
    ]
    reunioes = []

    for arquivo in arquivos_json:
        caminho_json = f'content/{arquivo}'
        if not os.path.exists(caminho_json):
            continue

        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)

        titulo = dados.get('título', '')
        tipo_limpo = arquivo.replace('meeting-', '').replace('.json', '')
        nome_base_csv = arquivo.replace('.json', '.csv')
        string_participantes = extrai_participantes_csv(f'content/{nome_base_csv}')

        data_reuniao_texto, pautas_dados = buscar_proxima_reuniao_e_issues(tipo_limpo, siglas, tasks)

        reunioes.append({
            'titulo': titulo,
            'dia': dados.get('Dia da semana', ''),
            'horario': dados.get('horário', ''),
            'participantes': string_participantes,
            'handson': dados.get('handons'),
            'proxima_data': data_reuniao_texto,
            'tem_pautas': bool(pautas_dados.get('pautas')),
            'pautas': pautas_dados.get('pautas', []),
            'erro_pautas': pautas_dados.get('erro', False)
        })

    return reunioes


def obter_nomes_estagiarios(tasks):
    estagiarios = set()
    for task in tasks:
        lista_est = task.get("estagiarios", [])
        if isinstance(lista_est, str):
            lista_est = [lista_est]
        for est in lista_est:
            if est and est != "Não Há":
                estagiarios.add(est.strip())
    return estagiarios


def formatar_grupo_issues(grupos, tasks):
    nomes = sorted(grupos.keys(), key=lambda x: (x == "Desativado", x.lower()))
    resultado = []

    for nome in nomes:
        grupos[nome].sort(key=lambda x: (x[1].get("data") or "", x[1].get("codigo", "")))
        issues_formatadas = []
        for task_codigo, issue in grupos[nome]:
            task = next((t for t in tasks if t["codigo"] == task_codigo), None)
            titulo = task.get("titulo", "") if task else "N/A"
            safe_id = re.sub(r"\s+", "_", nome.lower())
            responsaveis = task.get("responsaveis") if task else []
            responsaveis_tarefa = ", ".join(map(str, responsaveis))

            issues_formatadas.append({
                "task_codigo": task_codigo,
                "titulo_task": titulo,
                "responsaveis_tarefa": responsaveis_tarefa,
                "codigo_issue": re.sub(r'^[a-zA-Z]+', '', issue["codigo"]),
                "codigo_completo": issue["codigo"],
                "responsavel": nome,
                "safe_id": safe_id,
                "descricao": issue.get("descricao", ""),
                "data": issue.get("data", "")
            })

        resultado.append({
            "nome": nome,
            "safe_id": re.sub(r"\s+", "_", nome.lower()),
            "total_issues": len(issues_formatadas),
            "issues": issues_formatadas
        })

    return resultado


def preparar_dados_issues(tasks, issues):
    siglas = load_siglas()
    nomes_estagiarios = obter_nomes_estagiarios(tasks)

    grupos_func = defaultdict(list)
    grupos_est = defaultdict(list)
    nao_atribuidos = []

    for issue in issues:
        if issue.get("status") is not True:
            continue

        responsavel = issue.get("responsavel")
        codigo = issue["codigo"]
        task_codigo = codigo.split("-")[0]

        if not responsavel or not str(responsavel).strip():
            nao_atribuidos.append((task_codigo, issue))
            continue

        resp_str = str(responsavel).strip()
        if resp_str in nomes_estagiarios:
            grupos_est[resp_str].append((task_codigo, issue))
        else:
            grupos_func[resp_str].append((task_codigo, issue))

    issues_por_funcionario = formatar_grupo_issues(grupos_func, tasks)
    issues_por_estagiario = formatar_grupo_issues(grupos_est, tasks)

    nao_atribuidos_formatados = []
    if nao_atribuidos:
        nao_atribuidos.sort(key=lambda x: (x[1].get("data") or "", x[1].get("codigo", "")))
        for task_codigo, issue in nao_atribuidos:
            task = next((t for t in tasks if t["codigo"] == task_codigo), None)
            titulo = task.get("titulo", "") if task else "N/A"
            responsaveis = task.get("responsaveis") if task else []
            responsaveis_tarefa = ", ".join(map(str, responsaveis))
            match_pref = re.match(r"([a-zA-Z]+)", task_codigo)
            prefixo = match_pref.group(1) if match_pref else ""

            nao_atribuidos_formatados.append({
                "prefixo": prefixo,
                "significado": siglas.get(prefixo, ""),
                "task_codigo": task_codigo,
                "titulo_task": titulo,
                "responsaveis_tarefa": responsaveis_tarefa,
                "codigo_issue": re.sub(r'^[a-zA-Z]+', '', issue["codigo"]),
                "codigo_completo": issue["codigo"],
                "descricao": issue.get("descricao", ""),
                "data": issue.get("data", "")
            })

    return issues_por_funcionario, issues_por_estagiario, nao_atribuidos_formatados


def preparar_responsavel_summary(tasks):
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
        lista_est = task.get("estagiarios", [])
        if isinstance(lista_est, str):
            lista_est = [lista_est]

        for est in lista_est:
            if not est or est == "Não Há":
                continue
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

    prefixos_menu = []
    for prefix in sorted_prefixes:
        significado = siglas.get(prefix, "")
        label = f"{prefix} - {significado}" if significado else prefix
        prefixos_menu.append({
            "prefix": prefix,
            "label": label
        })

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
                    "descricao_html": latex_to_html(issue.get("descricao", ""))
                }
                for issue in related
            ]

            responsaveis_list = task.get("responsaveis", [task.get("responsavel", "")])
            responsaveis_str = "; ".join(responsaveis_list)
            estagiarios_str = "; ".join(task.get("estagiarios", []))

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
            "tasks": tasks_formatadas
        })

    return prefixos_menu, grupos_tarefas


def generate_html(tasks, issues, tutoriais, relatorios):
    siglas = load_siglas()
    reunioes = obter_dados_reunioes(siglas, tasks)
    issues_por_funcionario, issues_por_estagiario, issues_nao_atribuidas = preparar_dados_issues(tasks, issues)
    responsaveis_summary = preparar_responsavel_summary(tasks)
    estagiarios_summary = preparar_estagiario_summary(tasks)
    prefixos_menu, grupos_tarefas = preparar_grupos_tarefas(tasks, issues)

    template = jinja_env.get_template("index.html")
    return template.render(
        reunioes=reunioes,
        tutoriais=tutoriais,
        relatorios=relatorios,
        issues_por_funcionario=issues_por_funcionario,
        issues_por_estagiario=issues_por_estagiario,
        issues_nao_atribuidas=issues_nao_atribuidas,
        responsaveis_summary=responsaveis_summary,
        estagiarios_summary=estagiarios_summary,
        prefixos_menu=prefixos_menu,
        grupos_tarefas=grupos_tarefas
    )


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    processar_paginas()
    copy_assets()

    tasks = load_tasks()
    issues = load_issues(tasks)
    relatorios = processar_relatorios()
    tutoriais = processar_tutoriais()

    html = generate_html(tasks, issues, tutoriais, relatorios)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("Site e tutoriais gerados com sucesso em:", OUTPUT_DIR)


if __name__ == "__main__":
    main()