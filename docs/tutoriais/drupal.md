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
sudo apt-get install php php-common php-cli php-gd php-curl php-xml php-mbstring php-zip php-sybase php-mysql php-sqlite3
sudo apt-get install mariadb-server sqlite3 git
```

Instalação do php 7.4 para subir drupal da FFLCH (temporário):

```bash
sudo apt install apt-transport-https lsb-release ca-certificates curl -y
sudo wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg 
sudo sh -c 'echo "deb https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list'
sudo apt update
```

Instalação das dependências em php7.4:

```bash
sudo apt-get install php7.4 php7.4-common php7.4-cli php7.4-gd php7.4-curl php7.4-xml php7.4-mbstring php7.4-zip php7.4-sybase php7.4-sqlite3 php7.4-mysql
```

Trocar versão do php para 7.4:

```bash
sudo update-alternatives --set php /usr/bin/php7.4
sudo update-alternatives --set phar /usr/bin/phar7.4 
sudo update-alternatives --set phar.phar /usr/bin/phar.phar7.4 
```

Instalação do composer:

```bash
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

Criação de usuário admin com senha admin e criação de uma banco chamado drupal:
```bash
sudo mariadb
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%'  IDENTIFIED BY 'admin' WITH GRANT OPTION;
create database drupal;
quit
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
```

Subindo um server local:
```bash
cd drupal
./vendor/bin/drupal serve -vvv
# ou
./vendor/bin/drupal serve 0.0.0.0:8000 -vvv
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

Habilitando módulo treinamento:

```bash
./vendor/bin/drupal module:install treinamento
```
O comando a seguir vai gerar o controller TreinamentoController e a respectiva rota, no controller terá um método chamado index(), assim como uma rota /treinamento apontando para esse método:

```bash
./vendor/bin/drupal generate:controller  \
  --module="treinamento"  \
  --class="TreinamentoController"  \
  --routes='"title":"index", "name":"treinamento.index", "method":"index", "path":"/treinamento"'  \
  --no-interaction
```

Limpando cache:

```bash
./vendor/bin/drupal cc
```

### Exercício 1

Mostrar no seu controller quantidade de linhas do seguinte arquivo csv do tipo **rest**, **walking** e **running**. Também mostar a média da coluna **pulse** nos três casos **rest**, **walking** e **running**:

[https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv](https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv)

Exemplo de saída:

|  exercise.csv| rest  | walking   | running |
|--------------|-------|-----------|---------|
|  Qtde linhas |  XX   |     XX    |   XXX   | 
|  Média Pulse |  XX   |     XX    |   XXX   |

rest

## Dia 2

Rota com parâmetro, será injetada no método index do controller:

```bash
treinamento.index:
  path: '/treinamento/{parametro}'
  defaults:
    _controller: '\Drupal\treinamento\Controller\TreinamentoController::index'
  requirements:
    _permission: 'access content'
```

Criação de um twig template, para tal, criar um arquivo treinamento.module com a definição do template:

```php
/**
 * Implements hook_theme().
 */
function treinamento_theme($existing, $type, $theme, $path) {
  return [
    'treinamento' => [
      'variables' => ['parametro' => NULL],
    ],
  ];
}
```

Criação de um twig template em templates/treinamento.html.twig:

```html
<p>Nosso primeiro twig template!</p>
 
<p>Olha só o que você digitou na rota: {{ parametro }}</p>
```

Retornando o template no controller:
```php
    return [
      '#theme' => 'treinamento',
      '#parametro' => $parametro,
    ];
```

Na interface vamos criar alguns tipos de conteúdos.
Criando e deletando nodes de todos tipos para ambiente de desenvolvimento:

```bash
./vendor/bin/drupal create:nodes
./vendor/bin/drupal entity:delete node --all
```

Carregando id's dos nodes:

```bash
$nids = \Drupal::entityQuery('node')->condition('type','page')->execute();
```

**Desafio: Mostrar a quantidade de nodes do tipo selecionado**

Dica: pode-se desligar o cache de variáveis:
```php
return [
  '#theme' => 'treinamento',
    ...
  '#cache' => [
    'max-age' => 0,
  ],  
];
```

A partir dos **nids** pode-se carregar os objetos nodes:

```php
$nodes =  \Drupal\node\Entity\Node::loadMultiple($nids);
```

**Desafio: mostrar os títulos dos nodes no twig**

Criando um node do tipo page:
```php
use \Drupal\node\Entity\Node;

$node = Node::create([
    'type' => 'page',
    'title' => 'Teste com estagiários',
    'field_qualquer' => 123,
]);
$node->save();
```

Pode-se só manipular um node já existente:

```php
$nid = 1;
$node = \Drupal::entityTypeManager()->getStorage('node')->load($nid);
$node->save();
```

### Exercício 2

Neste exercício vamos continuar trabalhando com o seguinte arquivo:

[https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv](https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv)

- Criar um tipo de conteúdo com as colunas desse arquivo
- Criar uma rota e um controller que leia o arquivo csv e para cada linha crie um node correspondente no tipo de conteúdo criado anteriormente (se essa rota for clicada duas vezes, não duplicar registros, e sim atualizá-los)
- Criar uma rota, controller e template mostrando a tabela (a partir dos nodes e não do csv)
- Remontar a tabela do exercício 1, mas lendo os nodes: Mostrar no seu controller quantidade de linhas do seguinte arquivo csv do tipo **rest**, **walking** e **running**. Também mostar a média da coluna **pulse** nos três casos **rest**, **walking** e **running**:

Exemplo de saída:

|  exercise.csv| rest  | walking   | running |
|--------------|-------|-----------|---------|
|  Qtde linhas |  XX   |     XX    |   XXX   | 
|  Média Pulse |  XX   |     XX    |   XXX   |

## Dia 3

Instalação com perfil da fflch, **fflchprofile** e banco de dados mysql:
```bash
./vendor/bin/drush site-install fflchprofile \
    --db-url="mysql://admin:admin@localhost/drupal" \
    --site-name="fflch" \
    --site-mail="fflch@localhost" \
    --account-name="fflch" \
    --account-pass="fflch" \
    --account-mail="fflch@localhost" --yes
```

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



Criando e deletando nodes do tipo **agendamento** (deve ser criado na interface):

```bash
FALTA
```




