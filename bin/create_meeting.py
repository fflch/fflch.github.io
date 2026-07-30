import os
import json
import csv
import re
from datetime import datetime

# Configuração de Caminhos Base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_DIR = os.path.join(BASE_DIR, "files")
TASKS_DIR = os.path.join(BASE_DIR, "tasks")
ISSUES_DIR = os.path.join(TASKS_DIR, "issues")
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")
SIGLAS_PATH = os.path.join(FILES_DIR, "siglas.csv")


# ----------------------------------------
# Detecta os tipos de reuniões disponíveis na pasta files/
# ----------------------------------------
def listar_tipos_reuniao():
    tipos = []
    if os.path.exists(FILES_DIR):
        for f in os.listdir(FILES_DIR):
            # Procura por padrões 'meeting-XXX.json'
            if f.startswith("meeting-") and f.endswith(".json"):
                # Extrai apenas o termo correspondente (ex: 'laravel', 'drupal')
                tipo = f.replace("meeting-", "").replace(".json", "")
                tipos.append(tipo)
    tipos.sort()
    return tipos


# ----------------------------------------
# Busca o título da Task mãe (ex: tasks/bib001.json)
# ----------------------------------------
def obter_titulo_task_mae(nome_issue_arquivo):
    # Encontra o padrão do código da task (ex: de 'cci002-1.json' extrai 'cci002')
    match = re.match(r"^([a-zA-Z]+[0-9]+)", nome_issue_arquivo)
    if match:
        codigo_task = match.group(1)
        caminho_task = os.path.join(TASKS_DIR, f"{codigo_task}.json")
        
        if os.path.exists(caminho_task):
            try:
                with open(caminho_task, encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("titulo", "Sem título na Task")
            except:
                return "Erro ao ler título da Task"
                
    return "Task não encontrada"


# ----------------------------------------
# Carrega dicionário de siglas do CSV
# ----------------------------------------
def carregar_siglas():
    siglas = {}
    if os.path.exists(SIGLAS_PATH):
        with open(SIGLAS_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Pula cabeçalho
            for row in reader:
                if len(row) >= 2:
                    siglas[row[0].strip().lower()] = row[1].strip()
    return siglas


# ----------------------------------------
# Lista apenas as issues abertas (status == True)
# ----------------------------------------
def listar_issues_abertas():
    issues_abertas = []
    if not os.path.exists(ISSUES_DIR):
        return []

    for f in os.listdir(ISSUES_DIR):
        if f.endswith(".json"):
            caminho = os.path.join(ISSUES_DIR, f)
            try:
                with open(caminho, encoding="utf-8") as file:
                    data = json.load(file)
                    if data.get("status") is True:
                        issues_abertas.append({
                            "arquivo": f,
                            "descricao": data.get("descricao", "Sem descrição"),
                            "data": data.get("data", ""),
                            "responsavel": data.get("responsavel", "")
                        })
            except:
                pass
    
    issues_abertas.sort(key=lambda x: x["arquivo"])
    return issues_abertas


# ----------------------------------------
# Menu Interativo para Vincular Múltiplas Issues
# ----------------------------------------
def selecionar_issues(issues, dicionario_siglas):
    if not issues:
        print("\nℹ Nenhuma issue aberta encontrada no momento.")
        return []

    print("\nIssues abertas encontradas:\n")
    
    for i, issue in enumerate(issues, 1):
        nome_arquivo = issue["arquivo"]
        
        # Pega as letras iniciais para a sigla (ex: cci002-1.json -> cci)
        match_sigla = re.match(r"^([a-zA-Z]+)", nome_arquivo)
        sigla = match_sigla.group(1).lower() if match_sigla else ""
        significado_sigla = dicionario_siglas.get(sigla, "Desconhecido")
        
        # Busca o título diretamente de dentro do arquivo da Task mãe
        titulo_task = obter_titulo_task_mae(nome_arquivo)

        print(f"[{i:02d}] {nome_arquivo} → Task: {titulo_task} ({sigla.upper()} - {significado_sigla})")
        print(f"     Descrição: {issue['descricao']}")
        print("-" * 70)

    print("\nDigite os números das issues que deseja vincular separados por vírgula (Ex: 1,3).")
    print("Pressione Enter para pular sem vincular nenhuma.")
    
    while True:
        escolha = input("\nIssues selecionadas: ").strip()
        if not escolha:
            return []

        try:
            indices = [int(x.strip()) - 1 for x in escolha.split(",") if x.strip().isdigit()]
            if all(0 <= idx < len(issues) for idx in indices):
                return [issues[idx]["arquivo"] for idx in indices]
        except:
            pass

        print("Entrada inválida. Tente novamente.")


# ----------------------------------------
# MAIN
# ----------------------------------------
def main():
    print("\n--- Criação de Reunião Técnica ---")
    
    # 1. Seleção Dinâmica do Tipo de Reunião baseado na pasta files/
    tipos_disponiveis = listar_tipos_reuniao()
    if not tipos_disponiveis:
        print("⚠ Nenhuma configuração de reunião encontrada em files/ (padrão: meeting-*.json).")
        return
        
    print("\nSelecione o tipo de reunião:")
    for idx, tipo in enumerate(tipos_disponiveis, 1):
        print(f"{idx} - {tipo.capitalize()}")
        
    while True:
        escolha_tipo = input("\nEscolha o número correspondente: ").strip()
        if escolha_tipo.isdigit():
            opt_idx = int(escolha_tipo) - 1
            if 0 <= opt_idx < len(tipos_disponiveis):
                tipo_reuniao = tipos_disponiveis[opt_idx]
                break
        print("Opção inválida.")

    # 2. Entrada de Data da Reunião
    data_padrao = datetime.now().strftime("%Y-%m-%d")
    data_input = input(f"\nData da reunião (AAAA-MM-DD) [{data_padrao}]: ").strip()
    data_reuniao = data_input if data_input else data_padrao

    try:
        datetime.strptime(data_reuniao, "%Y-%m-%d")
    except ValueError:
        print("⚠ Formato de data inválido. Use AAAA-MM-DD.")
        return

    # 3. Carrega Siglas, procura Tasks correspondentes e vincula as Issues
    siglas = carregar_siglas()
    issues_abertas = listar_issues_abertas()
    issues_vinculadas = selecionar_issues(issues_abertas, siglas)

    # 4. Formatação dos Dados do JSON de Saída
    reuniao_dados = {
        "tipo": tipo_reuniao,
        "data": data_reuniao,
        "issues": issues_vinculadas
    }

    # 5. Salva o arquivo final
    os.makedirs(MEETINGS_DIR, exist_ok=True)
    nome_arquivo_reuniao = f"{tipo_reuniao}-{data_reuniao}.json"
    caminho_final = os.path.join(MEETINGS_DIR, nome_arquivo_reuniao)

    with open(caminho_final, "w", encoding="utf-8") as f:
        json.dump(reuniao_dados, f, indent=2, ensure_ascii=False)

    print(f"\n✔ Arquivo de reunião criado com sucesso em: {caminho_final}")


if __name__ == "__main__":
    main()