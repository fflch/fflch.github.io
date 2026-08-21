import requests
import json

# URL base e endpoint do módulo de contratações (Lei 14.133/2021)
url = "https://dadosabertos.compras.gov.br/modulo-contratacoes/1_consultarContratacoes_PNCP_14133"

# Parâmetros com base nos campos obrigatórios e no filtro da FFLCH
params = {
    "pagina": 1,
    "tamanhoPagina": 50,
    "unidadeOrgaoCodigoUnidade": "102108",   # UASG da FFLCH/USP
    "codigoModalidade": 6,                    # 6 = Pregão (ou 8 para Dispensa)
    "dataPublicacaoPncpInicial": "2025-01-01",
    "dataPublicacaoPncpFinal": "2025-12-31"
}


response = requests.get(url, params=params)
response.raise_for_status()

dados = response.json()

# A API costuma retornar uma lista direta ou um dicionário paginado
contratacoes = dados.get("resultado", []) if isinstance(dados, dict) else dados
    

if not contratacoes:
    print("Nenhuma contratação encontrada para os filtros aplicados.")
else:
    print(f"--- Foram encontradas {len(contratacoes)} contratações ---\n")
    for item in contratacoes:
        #print(json.dumps(item, indent=2, ensure_ascii=False))
        controle = item.get("numeroControlePNCP", "N/A")
        objeto = item.get("objetoCompra", "Sem descrição")
        valor = item.get("valorTotalHomologado", 0.0)

        print(f"PNCP: {controle} | Objeto: {objeto} | Valor: R$ {valor}")
