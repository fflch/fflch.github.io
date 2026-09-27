import glob
import json
import os
import re
import requests

# Configurações das páginas e prefixos de arquivos
ENV_CONFIGS = {
    "desenvolvimento": {
        "page_id": "3e7cd990-7222-807b-9223-c80cc73593c2",
        "prefixes": ("dev", "bib"),
    },
    "sites": {
        "page_id": "3e7cd990-7222-808fb7cec1e447098c97",
        "prefixes": ("cor", "mod"),
    },
}


def format_uuid(uuid_str):
  """Garante a formatação em UUID padrão com hífens."""
  clean = re.sub(r"[^a-fA-F0-9]", "", uuid_str)
  if len(clean) == 32:
    return (
        f"{clean[:8]}-{clean[8:12]}-{clean[12:16]}-{clean[16:20]}-{clean[20:]}"
    )
  return uuid_str


def clean_latex_text(text):
  """Remove marcadores do LaTeX e converte para texto/markdown limpo."""
  if not text:
    return ""

  text = re.sub(r"\\url\{([^}]+)\}", r"\1", text)
  text = re.sub(
      r"\\(begin|end)\{(itemize|enumerate)\}|\\bigskip|\\small|\\large",
      "",
      text,
  )
  text = re.sub(r"\\item\s*", "\n• ", text)
  text = text.replace("\\", "")
  text = re.sub(r"\n\s*\n", "\n", text).strip()

  return text


def extract_task_id(file_path):
  """Extrai o nome do arquivo sem extensão para usar como ID da task (ex: dev002)."""
  filename = os.path.basename(file_path)
  task_id, _ = os.path.splitext(filename)
  return task_id


def build_description_rich_text(data, task_id):
  """Monta a lista de objetos rich_text do Notion, aplicando link clicável na URL."""
  desc_clean = clean_latex_text(data.get("descricao", ""))
  responsaveis = ", ".join(data.get("responsaveis", []))
  estagiarios = ", ".join(data.get("estagiarios", []))

  parts = [desc_clean]

  if responsaveis:
    parts.append(f"\n\nResponsáveis: {responsaveis}")
  if estagiarios:
    parts.append(f"Estagiários: {estagiarios}")

  text_content = "\n".join(parts).strip()[:1900]

  rich_text = []

  # Adiciona o texto principal da descrição
  if text_content:
    rich_text.append({"type": "text", "text": {"content": text_content}})

  # Adiciona o link como hiperlink clicável do Notion
  if task_id:
    url = f"https://fflch.github.io/#{task_id}"
    prefix = "\n\nLink: " if text_content else "Link: "

    rich_text.append({"type": "text", "text": {"content": prefix}})
    rich_text.append(
        {"type": "text", "text": {"content": url, "link": {"url": url}}}
    )

  return rich_text


def get_headers(token):
  return {
      "Authorization": f"Bearer {token}",
      "Notion-Version": "2022-06-28",
      "Content-Type": "application/json",
  }


def find_existing_database(token, title, parent_id):
  """Busca se já existe um Kanban com o mesmo título dentro da página pai."""
  url = "https://api.notion.com/v1/search"
  payload = {
      "query": title,
      "filter": {"value": "database", "property": "object"},
  }

  try:
    res = requests.post(
        url, json=payload, headers=get_headers(token), timeout=10
    )
    if res.status_code == 200:
      clean_parent = parent_id.replace("-", "")
      for db in res.json().get("results", []):
        title_list = db.get("title", [])
        db_title = title_list[0].get("plain_text", "") if title_list else ""
        db_parent = (
            db.get("parent", {}).get("page_id", "").replace("-", "")
        )

        if db_title.strip() == title.strip() and db_parent == clean_parent:
          return db["id"]
  except Exception as e:
    print(f"Erro ao buscar '{title}': {e}")

  return None


def get_unlinked_child_pages(token, parent_id, processed_titles):
  """Busca todas as subpáginas ou child databases no Notion que não correspondem aos títulos processados."""
  url = f"https://api.notion.com/v1/blocks/{parent_id}/children"
  unlinked_pages = []
  has_more = True
  start_cursor = None

  while has_more:
    params = {}
    if start_cursor:
      params["start_cursor"] = start_cursor

    try:
      res = requests.get(
          url, headers=get_headers(token), params=params, timeout=10
      )
      if res.status_code != 200:
        print(f"Erro ao consultar filhos no Notion: {res.status_code}")
        break

      data = res.json()
      for block in data.get("results", []):
        block_type = block.get("type")
        title = ""

        if block_type == "child_page":
          title = block.get("child_page", {}).get("title", "")
        elif block_type == "child_database":
          title = block.get("child_database", {}).get("title", "")

        if title and title.strip() not in processed_titles:
          unlinked_pages.append(title.strip())

      has_more = data.get("has_more", False)
      start_cursor = data.get("next_cursor")

    except Exception as e:
      print(f"Erro ao buscar subpáginas não vinculadas: {e}")
      break

  return unlinked_pages


def update_kanban_database(token, database_id, description_rich_text):
  """Atualiza a descrição de um Kanban já existente com Rich Text."""
  url = f"https://api.notion.com/v1/databases/{database_id}"
  payload = {"description": description_rich_text}
  return requests.patch(
      url, json=payload, headers=get_headers(token), timeout=15
  )


def create_kanban_database(
    token, parent_id, board_title, description_rich_text
):
  """Cria um novo banco de dados Kanban com Rich Text na descrição."""
  url = "https://api.notion.com/v1/databases"

  payload = {
      "parent": {"type": "page_id", "page_id": parent_id},
      "icon": {"type": "emoji", "emoji": "📋"},
      "title": [{"type": "text", "text": {"content": board_title}}],
      "description": description_rich_text,
      "properties": {
          "Tarefa": {"title": {}},
          "Status": {
              "status": {
                  "options": [
                      {"name": "A Fazer", "color": "red"},
                      {"name": "Em Andamento", "color": "yellow"},
                      {"name": "Concluído", "color": "green"},
                  ]
              }
          },
          "Prioridade": {
              "select": {
                  "options": [
                      {"name": "Baixa", "color": "gray"},
                      {"name": "Média", "color": "blue"},
                      {"name": "Alta", "color": "red"},
                  ]
              }
          },
          "Responsável": {"people": {}},
          "Data Limite": {"date": {}},
      },
  }

  return requests.post(
      url, json=payload, headers=get_headers(token), timeout=15
  )


def create_sample_cards(token, database_id):
  """Cria tarefas iniciais de exemplo dentro do novo Kanban."""
  url = "https://api.notion.com/v1/pages"
  cards = [
      ("Levantamento de Requisitos", "A Fazer", "Alta"),
      ("Manutenção e Atualizações", "Em Andamento", "Média"),
      ("Testes de Usabilidade", "Concluído", "Baixa"),
  ]

  for title, status, priority in cards:
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Tarefa": {"title": [{"text": {"content": title}}]},
            "Status": {"status": {"name": status}},
            "Prioridade": {"select": {"name": priority}},
        },
    }
    requests.post(url, json=payload, headers=get_headers(token), timeout=10)


def main():
  print("==================================================")
  print("        SINCRONIZADOR DE TASKS — NOTION")
  print("==================================================\n")

  # 1. Pergunta qual ambiente sincronizar
  opcao = (
      input("Sincronizar desenvolvimento ou sites? [d/s]: ").strip().lower()
  )

  if opcao in ["desenvolvimento", "dev", "d"]:
    target_env = "desenvolvimento"
  elif opcao in ["sites", "site", "s"]:
    target_env = "sites"
  else:
    print("❌ Opção inválida. Digite 'desenvolvimento' ou 'sites'.")
    return

  config = ENV_CONFIGS[target_env]
  parent_id_formatted = format_uuid(config["page_id"])
  prefixes = config["prefixes"]

  # 2. Pergunta SOMENTE o token de integração
  token = input(
      "\nDigite seu Token de Integração do Notion (secret_...): "
  ).strip()
  if not token:
    print("Token não informado. Operação cancelada.")
    return

  # 3. Busca e filtra os arquivos JSON pelos prefixos definidos
  all_json_files = glob.glob("tasks/*.json")
  json_files = [
      f
      for f in all_json_files
      if os.path.basename(f).lower().startswith(prefixes)
  ]

  if not json_files:
    print(
        f"\n⚠️ Nenhum arquivo JSON correspondente aos prefixos {prefixes} foi"
        " encontrado em 'tasks/'."
    )
    return

  print(f"\nAmbiente Selecionado: {target_env.upper()}")
  print(f"Página Pai ID:        {parent_id_formatted}")
  print(
      f"Encontrado(s) {len(json_files)} arquivo(s) com prefixo {prefixes}...\n"
  )

  processed_titles = set()

  # 4. Processa cada arquivo JSON
  for file_path in sorted(json_files):
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        task_data = json.load(f)

      if task_data.get("status") is not True:
        continue

      title = task_data.get("titulo")
      if not title:
        continue

      processed_titles.add(title.strip())

      task_id = extract_task_id(file_path)
      description_rich_text = build_description_rich_text(task_data, task_id)

      existing_db_id = find_existing_database(
          token, title, parent_id_formatted
      )

      if existing_db_id:
        print(f"🔄 Atualizando descrição de '{title}' ({file_path})...")
        res = update_kanban_database(token, existing_db_id, description_rich_text)
        if res.status_code == 200:
          print(f"  ✓ '{title}' atualizado com sucesso!")
        else:
          print(f"  ❌ Erro ao atualizar ({res.status_code}): {res.text}")
      else:
        print(f"➕ Criando novo Kanban '{title}' ({file_path})...")
        res = create_kanban_database(
            token, parent_id_formatted, title, description_rich_text
        )
        if res.status_code == 200:
          db_id = res.json()["id"]
          create_sample_cards(token, db_id)
          print(f"  ✓ Quadro '{title}' criado com sucesso!")
        else:
          print(f"  ❌ Erro ao criar ({res.status_code}): {res.text}")

    except Exception as e:
      print(f"Erro ao processar {file_path}: {e}")

  # 5. Verifica subpáginas no Notion que não pertencem a nenhuma task ativa
  print(
      f"\n🔍 Verificando subpáginas não vinculadas no ambiente"
      f" '{target_env.upper()}'..."
  )
  unlinked_pages = get_unlinked_child_pages(
      token, parent_id_formatted, processed_titles
  )

  if unlinked_pages:
    print(
        f"\n⚠️ As seguintes páginas/databases no Notion NÃO fazem parte das"
        " suas tasks ativas:"
    )
    for p in unlinked_pages:
      print(f"  • {p}")
  else:
    print(
        "\n✅ Todas as subpáginas/databases no Notion correspondem a tasks"
        " ativas."
    )

  print("\nProcessamento concluído!")


if __name__ == "__main__":
  main()