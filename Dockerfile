# Etapa 1: gera o site estático em docs/
FROM python:3.12-slim AS build

RUN apt-get update \
    && apt-get install -y --no-install-recommends graphviz fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN rm -rf docs && python generate_site.py

# Etapa 2: serve apenas o conteúdo gerado
FROM nginx:1.27-alpine

COPY --from=build /app/docs /usr/share/nginx/html

EXPOSE 80
