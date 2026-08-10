import os
import json
import csv
import re
import subprocess
from datetime import datetime
import tempfile
import base64

# Configuração de Caminhos Base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_DIR = os.path.join(BASE_DIR, "content")
TASKS_DIR = os.path.join(BASE_DIR, "tasks")
MEETINGS_DIR = os.path.join(BASE_DIR, "meetings")
SIGLAS_PATH = os.path.join(FILES_DIR, "siglas.csv")


# ----------------------------------------
# Detecta os tipos de reuniões baseados na pasta files/
# ----------------------------------------
def listar_tipos_reuniao():
    tipos = []
    if os.path.exists(FILES_DIR):
        for f in os.listdir(FILES_DIR):
            if f.startswith("meeting-") and f.endswith(".json"):
                tipo = f.replace("meeting-", "").replace(".json", "")
                tipos.append(tipo)
    tipos.sort()
    return tipos


# ----------------------------------------
# Busca o título de uma Task Mãe
# ----------------------------------------
def obter_titulo_task_mae(nome_issue_arquivo):
    match = re.match(r"^([a-zA-Z]+[0-9]+)", nome_issue_arquivo)
    if match:
        codigo_task = match.group(1)
        caminho_task = os.path.join(TASKS_DIR, f"{codigo_task}.json")
        if os.path.exists(caminho_task):
            try:
                with open(caminho_task, encoding="utf-8") as f:
                    return json.load(f).get("titulo", "Sem título")
            except:
                pass
    return "Task não encontrada"


# ----------------------------------------
# Pega o Responsável e dados de uma Issue específica
# ----------------------------------------
def obter_dados_issue(nome_issue_arquivo):
    caminho_issue = os.path.join(TASKS_DIR, "issues", nome_issue_arquivo)
    if os.path.exists(caminho_issue):
        try:
            with open(caminho_issue, encoding="utf-8") as f:
                data = json.load(f)
                resp = data.get("responsavel", "Não atribuído")
                desc = data.get("descricao", "")
                return resp if resp else "Não atribuído", desc
        except:
            pass
    return "Não atribuído", ""


# ----------------------------------------
# Descobre a próxima reunião e formata a lista textual de pautas
# ----------------------------------------
def buscar_proxima_reuniao_dados(tipo_reuniao):

    hoje = datetime.now().date()
    reunioes_validas = []

    for f in os.listdir(MEETINGS_DIR):
        if f.startswith(f"{tipo_reuniao}-") and f.endswith(".json"):
            data_str = f.replace(f"{tipo_reuniao}-", "").replace(".json", "")
            try:
                data_reuniao = datetime.strptime(data_str, "%Y-%m-%d").date()
                if data_reuniao >= hoje:
                    reunioes_validas.append((data_reuniao, f))
            except ValueError:
                pass

    if not reunioes_validas:
        return None, None

    # Pega a mais próxima do futuro
    reunioes_validas.sort(key=lambda x: x[0])
    data_proxima, arquivo_proxima = reunioes_validas[0]
    data_formatada = data_proxima.strftime("%d/%m/%Y")
    
    texto_issues = ""
    try:
        with open(os.path.join(MEETINGS_DIR, arquivo_proxima), 'r', encoding='utf-8') as file:
            dados_reuniao = json.load(file)
            lista_issues = dados_reuniao.get("issues", [])
            lista_extra = dados_reuniao.get("extra", [])  # <--- Lê a lista de pautas extras
            
            # Se houver qualquer pauta (issue ou extra)
            if lista_issues or lista_extra:
                # 1. Adiciona as issues registradas
                for iss_arq in lista_issues:
                    responsavel, descricao = obter_dados_issue(iss_arq)
                    titulo_task = obter_titulo_task_mae(iss_arq)
                    texto_issues += f"- {titulo_task}: {descricao} ({responsavel})\n"
                
                # 2. Adiciona as pautas extras
                for item_extra in lista_extra:
                    texto_issues += f"- {item_extra}\n"
            else:
                texto_issues = "- Nenhuma pauta vinculada até o momento.\n"
    except:
        texto_issues = "- Erro ao ler a lista de pautas.\n"

    return data_formatada, texto_issues


# ----------------------------------------
# Extrai os e-mails da segunda coluna do CSV correspondente
# ----------------------------------------
def extrair_emails_csv(tipo_reuniao):
    caminho_csv = os.path.join(FILES_DIR, f"meeting-{tipo_reuniao}.csv")
    if not os.path.exists(caminho_csv):
        return []
    
    emails = []
    with open(caminho_csv, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 2:
                email = row[1].strip()
                if email:
                    emails.append(email)
    return emails

# ----------------------------------------
# Extrai os nomes do CSV correspondentes
# ----------------------------------------
def extrair_nomes_csv(tipo_reuniao):
    caminho_csv = os.path.join(FILES_DIR, f"meeting-{tipo_reuniao}.csv")
    if not os.path.exists(caminho_csv):
        return []
    
    nomes = []
    with open(caminho_csv, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 2:
                nome = row[0].strip()
                if nome:
                    nomes.append(nome)
    return nomes

def get_meeting(tipo):
    # Caminho para a pasta onde estão os arquivos
    pasta = FILES_DIR
    
    # Formata o nome do arquivo com base no tipo (ex: 'ti' vira 'meeting-ti.json')
    nome_arquivo = f"meeting-{tipo.lower()}.json"
    caminho_completo = os.path.join(pasta, nome_arquivo)
    
    with open(caminho_completo, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
        return dados
    
# ----------------------------------------
# MAIN
# ----------------------------------------
def main():
    print("\n--- Preparar E-mail de Convocação (Mutt) ---")
    
    tipos_disponiveis = listar_tipos_reuniao()
    if not tipos_disponiveis:
        print("Nenhuma configuração de reunião localizada na pasta files/.")
        return
        
    for idx, tipo in enumerate(tipos_disponiveis, 1):
        print(f"{idx} - {tipo.capitalize()}")
        
    while True:
        escolha = input("\nEscolha o número correspondente ao tipo de reunião: ").strip()
        if escolha.isdigit():
            opt_idx = int(escolha) - 1
            if 0 <= opt_idx < len(tipos_disponiveis):
                tipo_reuniao = tipos_disponiveis[opt_idx]
                break
        print("Opção inválida.")

    # 1. Busca a próxima reunião e pautas
    dados_reuniao = buscar_proxima_reuniao_dados(tipo_reuniao)
    
    if not dados_reuniao or not dados_reuniao[0]:
        print(f"\nℹ Nenhuma reunião de {tipo_reuniao.capitalize()} agendada a partir de hoje. Abortando.")
        return
        
    data_reuniao, lista_pautas = dados_reuniao
    horario = get_meeting(tipo_reuniao)['horário']

    # 2. Extrai os destinatários do CSV correspondente
    lista_emails = extrair_emails_csv(tipo_reuniao)
    if not lista_emails:
        print(f"⚠ Nenhum e-mail encontrado em files/meeting-{tipo_reuniao}.csv.")
        return
    
    destinatarios = ", ".join(lista_emails)
    lista_nomes = extrair_nomes_csv(tipo_reuniao)

    # 3. Monta o corpo do texto do e-mail
    corpo_email = f"""{', '.join(lista_nomes[:-1]) + ' e ' + lista_nomes[-1] if len(lista_nomes) > 1 else lista_nomes[0]},

No dia {data_reuniao}, {horario}, teremos nossa reunião de {tipo_reuniao.capitalize()}. Os itens abaixo serão abordados, se tiverem algo para adicionar, alterar ou remover me respondam esse email.

Pautas da Reunião:

{lista_pautas}
Lembrem que o planejamento das reuniões pode ser visto em: https://fflch.github.io
"""

    texto_assunto = f"Reunião {data_reuniao} - {tipo_reuniao.capitalize()}"
    texto_encoded = base64.b64encode(texto_assunto.encode('utf-8')).decode('utf-8')
    assunto = f"=?utf-8?B?{texto_encoded}?="

    print(f"\nReunião localizada para o dia {data_reuniao}.")
    print(f"Preparando Mutt para enviar para: {len(lista_emails)} destinatários...")

    # Cria um arquivo temporário com o corpo do e-mail
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
        # Adiciona cabeçalhos de codificação para o Mutt/Vim não se perderem
        temp_file.write("MIME-Version: 1.0\n")
        temp_file.write("Content-Type: text/plain; charset=utf-8\n")
        temp_file.write(f"Subject: {assunto}\n")
        temp_file.write(f"To: {destinatarios}\n\n") # Duas quebras de linha separam o cabeçalho do corpo

        temp_file.write(corpo_email)
        temp_path = temp_file.name

    subprocess.run(["mutt", "-H", temp_path])

    # Remove o arquivo temporário após fechar o Mutt
    if os.path.exists(temp_path):
        os.remove(temp_path)


if __name__ == "__main__":
    main()