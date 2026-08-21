def gerar_url_edital():
    while True:
        chave = input("\nDigite a chave PNCP (ou 'sair' para encerrar): ").strip()
        
        if chave.lower() in ['sair', 'exit', 'q']:
            print("Encerrando...")
            break
            
        if not chave:
            continue

        try:
            # Parse da chave (Ex: 63025530000104-1-000246/2025)
            cnpj, resto = chave.split("-", 1)
            _, resto = resto.split("-", 1)
            sequencial_str, ano_str = resto.split("/")
            
            sequencial = int(sequencial_str)  # Converte para int para remover zeros à esquerda
            ano = int(ano_str)

            # Monta a URL direta da página do edital
            url_edital = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
            
            print(f"URL do Edital: {url_edital}")

        except ValueError:
            print("Formato de chave inválido! Use o padrão: 63025530000104-1-000246/2025")

if __name__ == "__main__":
    gerar_url_edital()