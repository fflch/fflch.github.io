---
layout: default
title: Pixelfed
parent: Tutoriais
nav_order: 6
---
1. TOC
{:toc}
---

# Pixelfed: Configuração e Desenvolvimento

## Realizando a instalação do pixelfed.

Antes de qualquer coisa lembre-se de ter na sua máquina o Redis instalado, além do php e todas as ferramentas atreladas ao contexto de desenvolvimento como um banco de dados, seja mysql, mariadb ou postgresql.

Instale o Redis, como seguinte comando:
```bash
sudo apt install redis-server
```

Para verificar se ele está funcionando utilize o seguinte comando:

```bash
redis-cli ping
```

Deve retornar a palavra PONG no terminal. Pode utilizar as ferramentas de controle do sistema do linux. Exemplo:

```bash
sudo systemctl status redis
```
Agora é necessário configurar o banco de dados que iremos utilizar para o pixelfed. (Algumas dessas informações podem ser verificadas no site oficial).

Aqui neste tutorial estaremos utilizando o MariaDB, Caso já possua instalado um banco de sua preferêcia apenas crie o banco que irá utilizar na sua aplicação. Siga o processo abaixo:

```bash
sudo apt install mariadb-server mariadb-client

sudo systemctl start mariadb # para caso o serviço não tenha iniciado.
sudo systemctl status mariadb # para verificar o estado do serviço.

sudo mariadb
```

Agora crie a instância do banco que irá utilizar, fique a vontade com os nomes estaremos utilizando pixelfed, a senha é de seu encargo.

```java

CREATE DATABASE pixelfed CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'pixelfed'@'localhost' IDENTIFIED BY 'senha_de_sua_escolha';

GRANT ALL PRIVILEGES ON pixelfed.* TO 'pixelfed'@'localhost';

FLUSH PRIVILEGES;

EXIT;
```

Tudo pronto podemos dar início ao desenvolvimento com um fork do repositório oficial do pixelfed.

```bash 
git clone git@github.com:pixelfed/pixelfed.git
```

Após clonar o diretório diretamente do repositório oficial do pixelfed, siga para o diretorio salvo na sua máquina. Utilize o comando:

```bash 
cd pixelfed
```
Em seguida utilize o `Composer` para instalar os pacotes necessários para o execução da aplicação. Os comandos `--no-ansi` `--no-interaction` `--optimize-autoloader`, servem argumentos para a execução do comando install, definem respectivamente a realizar o comando sem a utilização de cores ansi do terminal, realizar o comando sem interações do usuário (perguntas de "*yes*" ou "*no*" que podem surgir) e a otimização da execução do comando utilizado.

```bash
composer install --no-ansi --no-interaction --optimize-autoloader
```
Agora copie o `.env.example`, a fim de ter seu próprio arquivo .env, utilize o seguinte comando:

```bash 
cp .env.example .env
```
Após esse processo será necessário configurar o `.env` para o funcionamento adequado e correto. Esse deve ser o contéudo presente no `.env` inicialmente:

```bash
APP_NAME="Pixelfed"
APP_ENV="production"
APP_KEY=
APP_DEBUG="false"

# Instance Configuration
OPEN_REGISTRATION="false"
ENFORCE_EMAIL_VERIFICATION="false"
PF_MAX_USERS="1000"
OAUTH_ENABLED="true"
ENABLE_CONFIG_CACHE="true"
INSTANCE_DISCOVER_PUBLIC="true"

# Media Configuration
PF_OPTIMIZE_IMAGES="true"
IMAGE_QUALITY="80"
MAX_PHOTO_SIZE="15000"
MAX_CAPTION_LENGTH="500"
MAX_ALBUM_LENGTH="4"

# Instance URL Configuration
APP_URL="http://localhost"
APP_DOMAIN="localhost"
ADMIN_DOMAIN="localhost"
SESSION_DOMAIN="localhost"
TRUST_PROXIES="*"

# Database Configuration
DB_CONNECTION="mysql"
DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_DATABASE="pixelfed"
DB_USERNAME="pixelfed"
DB_PASSWORD="pixelfed"

# Redis Configuration
REDIS_CLIENT="predis"
REDIS_SCHEME="tcp"
REDIS_HOST="127.0.0.1"
REDIS_PASSWORD="null"
REDIS_PORT="6379"

# Laravel Configuration
SESSION_DRIVER="database"
CACHE_DRIVER="redis"
QUEUE_DRIVER="redis"
BROADCAST_DRIVER="log"
LOG_CHANNEL="stack"
HORIZON_PREFIX="horizon-"

# ActivityPub Configuration
ACTIVITY_PUB="false"
AP_REMOTE_FOLLOW="false"
AP_INBOX="false"
AP_OUTBOX="false"
AP_SHAREDINBOX="false"

# Experimental Configuration
EXP_EMC="true"

## Mail Configuration (Post-Installer)
MAIL_DRIVER=log
MAIL_HOST=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
MAIL_FROM_ADDRESS="pixelfed@example.com"
MAIL_FROM_NAME="Pixelfed"

## S3 Configuration (Post-Installer)
PF_ENABLE_CLOUD=false
FILESYSTEM_CLOUD=s3
#AWS_ACCESS_KEY_ID=
#AWS_SECRET_ACCESS_KEY=
#AWS_DEFAULT_REGION=
#AWS_BUCKET=<BucketName>
#AWS_URL=
#AWS_ENDPOINT=
#AWS_USE_PATH_STYLE_ENDPOINT=false
```
Note que no .env gerado existe um atributo chamado `APP_KEY`, logo é necessário gerar uma chave para que a aplicação funcione corretamente.

```bash
php artisan key:generate
```

Feito isto é necessário rodar as migrations para que todas as configurações do banco estejam presente também no nosso espaço de desenvolvimento, por isso devemos configurar o endereço corretamente dos serviços no arquivo .env, segue um exemplo funcional abaixo.

```bash
APP_NAME="Pixelfed"
APP_ENV="local"
APP_KEY=gere_a_chave_com_o_comando_indicado_anteriormente
APP_DEBUG="true"

# Instance Configuration
OPEN_REGISTRATION="false"
ENFORCE_EMAIL_VERIFICATION="false"
PF_MAX_USERS="1000"
OAUTH_ENABLED="true"
ENABLE_CONFIG_CACHE="true"
INSTANCE_DISCOVER_PUBLIC="true"

# Media Configuration
PF_OPTIMIZE_IMAGES="true"
IMAGE_QUALITY="80"
MAX_PHOTO_SIZE="15000"
MAX_CAPTION_LENGTH="500"
MAX_ALBUM_LENGTH="4"

# Instance URL Configuration
APP_URL="http://localhost:8000"
APP_DOMAIN="localhost"
ADMIN_DOMAIN="localhost"
SESSION_DOMAIN="localhost"
TRUST_PROXIES="*"
FORCE_HTTPS_URLS=false
SESSION_SECURE_COOKIE=false

# Database Configuration
DB_CONNECTION="mariadb"
DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_DATABASE="pixelfed"
DB_USERNAME="pixelfed"
DB_PASSWORD="senha_criada_para_o_usuario_no_banco_de_dados"

# Redis Configuration
REDIS_CLIENT="predis"
REDIS_SCHEME="tcp"
REDIS_HOST="127.0.0.1"
REDIS_PASSWORD="null"
REDIS_PORT="6379"

# Laravel Configuration
SESSION_DRIVER="redis"
CACHE_DRIVER="redis"
QUEUE_DRIVER="redis"
BROADCAST_DRIVER="redis"
LOG_CHANNEL="stack"
HORIZON_PREFIX="horizon-"

# ActivityPub Configuration
ACTIVITY_PUB="false"
AP_REMOTE_FOLLOW="false"
AP_INBOX="false"
AP_OUTBOX="false"
AP_SHAREDINBOX="false"

# Experimental Configuration
EXP_EMC="true"

## Mail Configuration (Post-Installer)
MAIL_DRIVER=log
MAIL_HOST=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
MAIL_FROM_ADDRESS="pixelfed@example.com"
MAIL_FROM_NAME="Pixelfed"

## S3 Configuration (Post-Installer)
PF_ENABLE_CLOUD=false
FILESYSTEM_CLOUD=s3
#AWS_ACCESS_KEY_ID=
#AWS_SECRET_ACCESS_KEY=
#AWS_DEFAULT_REGION=
#AWS_BUCKET=<BucketName>
#AWS_URL=
#AWS_ENDPOINT=
#AWS_USE_PATH_STYLE_ENDPOINT=false

# Chat e Notificações
PF_CHAT_ENABLED=true
PF_CHAT_SYSTEM=redis
PF_CHAT_NOTIFICATIONS=true
PF_CHAT_MAX_LENGTH=1000
PF_CHAT_RATE_LIMIT=10

# Follow System
PF_FOLLOW_AUTO_ACCEPT=true
PF_FOLLOW_RATE_LIMIT=30
PF_FOLLOW_DOMAIN_BLOCKLIST=

# Redis para broadcasting
BROADCAST_DRIVER=redis
REDIS_BROADCAST_HOST=127.0.0.1
REDIS_BROADCAST_PORT=6379

# Cache para contadores
PF_CACHE_FOLLOW_COUNTS=true
PF_CACHE_FOLLOW_TTL=300

# API e Eventos
PF_API_RATE_LIMIT=300
PF_EVENTS_ENABLED=true
PF_REAL_TIME_UPDATES=true
```
É muito importante que a variável `FORCE_HTTPS_URLS` seja false. O pixelfed tem restrições de domínio para Https que são chatas e atrapalham no desenvolvimento local.

Agora vamos rodar as migrations via Artisan, lembre-se que o banco deve já ter sido criado previamente e deve estar corretamente especificado no .env, utilize o seguinte comando:

```bash
php artisan migrate --force
```
Migrations realizadas. Tudo pronto para iniciar o seu serviço local com o Pixelfed.

Tudo pronto para iniciar o servidor e começar a desenvolvimento da sua aplicação! Utilize o comando a seguir para criar chaves de autenticação de oauth:

```bash
php artisan passport:keys --force
```

Agora é necessário dizer para a sua aplicação que alguns arquivos que não são públicos sejam expostos, então o comando a serguir serve para criar um link simbólico para o acesso a tais arquivos:

```bash
php artisan storage:link
```

Agora utilize o comando de inicialização do servidor via Artisan para que possamos testar a aplicação.

```bash
php artisan serve --host=0.0.0.0
```
O parâmetro `--host`, delimita os valores que endereçam a aplicação no nosso servidor artisan. Caso não fosse definido tal parâmetro haveria um conflito, pois especificamos no `.env` que a aplicação está endereçada por localhost, logo o servidor seria incapaz de localizar o localhost, por seu padrão de endereçamento ser 127.0.0.1. Assim também se faz necessário especificar a porta.

Agora vamos criar um usuário admin e um usuário comum para os testes. 

Utilizando o comando:

```bash
php artisan user:create
```
Siga o que a imagem a baixo indica para criar um usuário.

![user_create_img](/assets/images/pixelfed/user_create.png)

Para criar um usuário sem as autorizações de admin basta responder não na criação do mesmo.
