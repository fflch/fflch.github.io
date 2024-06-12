---
layout: default
title: Drupal
parent: Tutoriais
nav_order: 4
---
1. TOC
{:toc}
---

# Treinamento Drupal

## Dia 1

### Instalação 

Biblioteca mínimas para instalação no debian 12:

```bash
apt-get install php php-common php-cli php-gd php-curl php-xml php-mbstring php-zip php-sybase
apt-get install mariadb-server php-mysql sqlite3 php-sqlite3
```

Instalação do composer:

```bash
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

Instalação do mariadb e criação de usuário admin com senha admin e criação de uma banco chamado drupal:
```bash
sudo apt install mariadb-server
sudo mariadb
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%'  IDENTIFIED BY 'admin' WITH GRANT OPTION;
create database drupal;
quit
exit
```

Instalação da distribuição Drupal da FFLCH: 

```bash
git clone git@github.com:SEU-USERNAME/drupal.git
cd drupal
composer install
```

Instalação do Drupal com sqlite e perfil padrão:

```bash
./vendor/bin/drush site-install standard \
    --db-url=sqlite://sites/default/files/.ht.sqlite \
    --site-name="fflch" \
    --site-mail="fflch@localhost" \
    --account-name="fflch" \
    --account-pass="fflch" \
    --account-mail="fflch@localhost" --yes
composer install
```

Instalação com perfil da fflch, **fflchprofile** e banco de dados mysql:
```bash
./vendor/bin/drush site-install fflchprofile \
    --db-url="mysql://admin:admin@localhost/drupal" \
    --site-name="fflch" \
    --site-mail="fflch@localhost" \
    --account-name="fflch" \
    --account-pass="fflch" \
    --account-mail="fflch@localhost" --yes
composer install
```

Subindo um server local:
```bash
cd drupal
./vendor/bin/drupal serve -vvv
# ou
./vendor/bin/drupal serve 0.0.0.0:8000 -vvv
```

Criando e deletando nodes de todos tipos para ambiente de desenvolvimento:

```bash
./vendor/bin/drupal create:nodes
./vendor/bin/drupal entity:delete node --all
```

Criando e deletando nodes do tipo **agendamento** (deve ser criado na interface):

```bash
FALTA
```

Zerando banco de dados:
```bash
# sqlite
# mysql
./vendor/bin/drupal database:drop

# sqlite
rm web/sites/default/files/.ht.sqlite*
```

### Criação de módulo:

Criação de um módulo chamado treinamento:

```bash
./vendor/bin/drupal generate:module  \
  --module="treinamento"  \
  --machine-name="treinamento"  \
  --module-path="modules"  \
  --description="Módulo Treinamento"  \
  --core="8.x"  \
  --no-interaction
```

Habilitando módulo

```bash
Falta
```

As entradas de rotas são definidas em **treinamento.routing.yml**, no caso o controller será TreinamentoController com um método chamado **index**:

```bash
treinamento.index:
  path: '/treinamento'
  defaults:
    _controller: '\Drupal\treinamento\Controller\TreinamentoController::index'
  requirements:
    _permission: 'access content'
```

O comando a seguir vai gerar o controller TreinamentoController com um método chamado index(), assim como uma rota /treinamento apontando para esse método:

```bash
./vendor/bin/drupal generate:controller  \
  --module="treinamento"  \
  --class="TreinamentoController"  \
  --routes='"title":"index", "name":"treinamento.index", "method":"index", "path":"/treinamento"'  \
  --no-interaction
```

Rota com parâmetro:

```bash
treinamento.index:
  path: '/treinamento/{parametro}'
  defaults:
    _controller: '\Drupal\treinamento\Controller\TreinamentoController::index'
  requirements:
    _permission: 'access content'
```
### Exercício 1

Mostrar no seu controller quantas linhas do seguinte arquivo csv tem o tipo **rest** e quantas linhas tem o tipo **walking**, para ambos mostrar a média da coluna **pulse**:

[https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv](https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv)

## Dia 2
No controller, retornar um template twig:

```bash
FALTA
```

Criação de node sistematicamente:

```bash
FALTA
```

Criação de node sistematicamente com arquivo pdf em anexo:

```bash
FALTA
```

Criação de node sistematicamente com múltiplos arquivo pdfs em anexo:

```bash
FALTA
```

Submissão de webform sistematicamente:

```bash
FALTA
```




