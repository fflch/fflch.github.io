import csv
import json
import requests

# Base da URL do módulo PNCP (Lei 14.133/2021)
url = "https://dadosabertos.compras.gov.br/modulo-contratacoes/1_consultarContratacoes_PNCP_14133"

# 1. Pergunta o código da unidade (Default: FFLCH - 102108, STI 102167)
unidade_input = input(
    "Informe o código da unidade/UASG [Padrão: 102108 - FFLCH]: "
).strip()
unidade = unidade_input if unidade_input else "102108"

# 2. Pergunta a modalidade (Padrão: 6 - Dispensa)
print("\nModalidades principais:")
print("5 - Pregão | 6 - Dispensa | 7 - Inexigibilidade")
modalidade_input = input("Informe o código da modalidade [Padrão: 6]: ").strip()
modalidade = int(modalidade_input) if modalidade_input.isdigit() else 6

# 3. Pergunta o ano e monta o período de publicação
ano_input = input("\nInforme o ano para pesquisa [Ex: 2025]: ").strip()
ano = ano_input if ano_input else "2025"
data_inicial = f"{ano}-01-01"
data_final = f"{ano}-12-31"

# 5. Pergunta sobre a exportação em CSV
salvar_csv_resp = (
    input("\nDeseja salvar o resultado em um arquivo CSV? (s/N): ")
    .strip()
    .lower()
)
salvar_csv = salvar_csv_resp.startswith("s")

# Lista para armazenar todos os registros recuperados entre as páginas
todas_contratacoes = []
pagina_atual = 1
total_paginas = 1  # Será atualizado na primeira requisição

print("\nIniciando busca nos servidores do Compras.gov.br...\n")

# 4. Loop para iterar por todas as páginas disponíveis
while pagina_atual <= total_paginas:
    params = {
        "pagina": pagina_atual,
        "tamanhoPagina": 50,
        "unidadeOrgaoCodigoUnidade": unidade,
        "codigoModalidade": modalidade,
        "dataPublicacaoPncpInicial": data_inicial,
        "dataPublicacaoPncpFinal": data_final,
    }

    try:
        response = requests.get(url, params=params)
        print(response.url)
        response.raise_for_status()
        dados = response.json()

        # Extração do resultado e metadados de paginação
        if isinstance(dados, dict):
            contratacoes = dados.get("resultado", [])
            # A API retorna 'totalPaginas' nos metadados da resposta
            total_paginas = dados.get("totalPaginas", total_paginas)
        else:
            contratacoes = dados
            total_paginas = 1

        if not contratacoes:
            break

        todas_contratacoes.extend(contratacoes)
        print(
            f"Página {pagina_atual} de {total_paginas} processada... ({len(contratacoes)} itens)"
        )

        pagina_atual += 1

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar a página {pagina_atual}: {e}")
        break

# Exibição dos resultados e salvamento
if not todas_contratacoes:
    print("\nNenhuma contratação encontrada para os filtros aplicados.")
else:
    print(
        f"\n--- TOTAL ENCONTRADO: {len(todas_contratacoes)} contratações ---\n"
    )

    for item in todas_contratacoes:
        controle = item.get("numeroControlePNCP", "N/A")
        objeto = item.get("objetoCompra", "Sem descrição")
        valor = item.get("valorTotalHomologado", 0.0)

        print(f"PNCP: {controle} | Objeto: {objeto} | Valor: R$ {valor}")

    # Geração do arquivo CSV caso solicitado
    if salvar_csv:
        nome_arquivo = f"contratacoes_{unidade}_{ano}.csv"
        try:
            with open(
                nome_arquivo, mode="w", newline="", encoding="utf-8-sig"
            ) as arquivo_csv:
                writer = csv.writer(arquivo_csv, delimiter=";")

                # Escreve o cabeçalho
                writer.writerow(["PNCP", "Objeto", "Valor Total Homologado"])

                # Escreve cada linha de dados
                for item in todas_contratacoes:
                    writer.writerow(
                        [
                            item.get("numeroControlePNCP", "N/A"),
                            item.get("objetoCompra", "Sem descrição"),
                            item.get("valorTotalHomologado", 0.0),
                        ]
                    )

            print(f"\n[SUCESSO] Arquivo salvo em: {nome_arquivo}")
        except IOError as e:
            print(f"\n[ERRO] Falha ao gravar o arquivo CSV: {e}")