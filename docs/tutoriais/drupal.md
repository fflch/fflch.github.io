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

Biblioteca mínimas para instalação no Debian 12:

```bash
sudo apt-get install php php-common php-cli php-gd php-curl php-xml php-mbstring php-zip php-sybase php-mysql php-sqlite3
sudo apt-get install mariadb-server sqlite3 git
```

Instalação do composer:

```bash
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

Configuração do banco de dados
```bash
sudo mariadb
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%'  IDENTIFIED BY 'admin' WITH GRANT OPTION;
create database drupal;
quit
```

Instalação do Drupal
```bash
composer create-project drupal/recommended-project site-treinamento
cd site-treinamento
composer require drush/drush
./vendor/bin/drush --version
```

Criação de um site Drupal:

```bash
./vendor/bin/drush site:install standard \
  --db-url="mysql://admin:admin@localhost/drupal" \
  --site-name="Site Treinamento" \
  --account-name="admin" \
  --account-pass="admin" --yes
```

Subindo um server local:
```bash
./vendor/bin/drush rs 0.0.0.0:8000
```

### Criação de módulo:

Criação de um módulo chamado `treinamento`:

```bash
./vendor/bin/drush generate module
```

Habilitando módulo treinamento

```bash
./vendor/bin/drush pm-install treinamento
```

O comando a seguir vai gerar o controller TreinamentoController e a respectiva rota, no controller terá um método chamado index(), assim como uma rota /treinamento apontando para esse método:

```bash
./vendor/bin/drush generate controller
​
Module machine name:
➤ treinamento

Class [TreinamentoController]
➤ TreinamentoController
​
Route name [treinamento.example]:
➤ treinamento.index
​
Route path [/treinamento/index]:
➤ /treinamento 
```

Limpando cache:
```bash
./vendor/bin/drush cr
```

### twig

Crie o arquivo treinamento.html.twig e coloque um html qualquer nele:
```bash
mkdir web/modules/treinamento/templates
touch web/modules/treinamento/templates/index.html.twig
```

```php
public function index() {
  $variavel1 = 'bom dia';
  $variavel2 = 'boa noite';

  return [
    '#theme' => 'index',
    '#variavel1' => $variavel1,
    '#variavel2' => $variavel2,
  ];
}
```

Por fim, criar um arquivo treinamento.module com a definição do template:

```php
<?php

/**
 * Implements hook_theme().
 */
function treinamento_theme($existing, $type, $theme, $path) {
  return [
    'index' => [
      'variables' => [
        'variavel1' => NULL,
        'variavel2' => NULL
        ],
    ],
  ];
}
```

Twig é um motor de templates moderno para PHP que o Drupal utiliza, exemplo:

```php
{% raw %}
{% if date("H") < 12  %}
    {{ variavel1 }}
{% else %}
    {{ variavel2 }}
{% endif %}
{% endraw %}
```

### Exercício 1

## Exercício 1 - Importação de Dados e Estatísticas com Laravel

**Objetivo**: Importar dados de um arquivo CSV e exibir estatísticas desses dados no Drupal.

[https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv](https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv)

1) Criar o Controller e a Rota para Importação

- Crie um controller chamado ExerciseController com o método importCsv.
- Defina uma rota `exercises/importcsv` que aponte para o método importCsv do controller.
- No método importCsv, implemente a lógica para ler o arquivo `exercise.csv`.

Dica: Você pode usar a classe `League\Csv\Reader` (disponível via Composer) para facilitar a leitura do CSV.

2) Após ler o arquivo, apresente as seguintes estatísticas:

- quantidades de linhas da coluna pulse para os casos rests, walking e running
- calcule as média da coluna pulse para os casos rests, walking e running, conforme tabela abaixo

Exemplo de saída:

|  exercise.csv| rest  | walking   | running |
|--------------|-------|-----------|---------|
|  Qtde linhas |  XX   |     XX    |   XXX   | 
|  Média Pulse |  XX   |     XX    |   XXX   |

<!--
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

Iterando sob a os objetos nodes no twig:
```php
<ul>
    {% for node in p %}
        <li>{{ node.title.value }} - {{ node.field_autor.value }}</li>
    {% endfor %}
</ul>
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

Ou se preferir:

```php
use \Drupal\node\Entity\Node;

$node = Node::create(['type' => 'page']);
$node->title = 'mais um node';
$node->field_qualquer= 'Teste com estagiários';
$node->save();
```

Pode-se manipular somente um node já existente:

```php
$nid = 1;
$node = Node::load($nid);
$node->body->format = 'full_html';
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

Criação de usuário admin com senha admin e criação de uma banco chamado drupal:
```bash
sudo mariadb
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%'  IDENTIFIED BY 'admin' WITH GRANT OPTION;
create database drupal;
quit
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
```

Como chamar um script php usando linha de comando, útil, por exemplo,  para criar nodes sistematicamente:

```bash
./vendor/bin/drush php-script ~/cria_nodes.php
```

Carregando arquivo ao criar um node:

```php
use \Drupal\node\Entity\Node;

$data = file_get_contents('/home/thiago/arquivo.pdf');
$file = file_save_data($data, 'public://arquivo.pdf', FILE_EXISTS_REPLACE);

$node = Node::create([
    'type' => 'page',
    'title' => 'Teste com arquivo',
    'field_arquivo' => [
        'target_id' => $file->id(),
        'alt' => 'Pdf exemplo',
        'title' => 'Pdf exemplo'
    ],
]);

$node->save();
```

Outra forma de carregar um arquivo:
```php
use \Drupal\node\Entity\Node;
use \Drupal\file\Entity\File;

$filepath = '/home/thiago/arquivo.pdf';
$file = File::create([
  'filename' => basename($filepath),
  'uri' => 'public://' . basename($filepath),
  'status' => 1,
  'uid' => 1,
]);
$file->save();

$node = Node::create([
    'type' => 'page',
    'title' => 'Teste com arquivo',
    'field_arquivo' => [
        'target_id' => $file->id(),
        'alt' => 'Pdf exemplo',
        'title' => 'Pdf exemplo'
    ],
]);

$node->save();
```
Se quiser especificar uma pasta em files, troque 'public://' por 'public://MINHA-PASTA/'

Criação de uma submissão de um webform:

```bash
use Drupal\webform\Entity\Webform;
use Drupal\webform\Entity\WebformSubmission;

$webform_id = 'meu_webform';
$webform = Webform::load($webform_id);

$values = [
  'webform_id' => $webform->id(),
  'data' => [
    'nome' => 'Thiago Gomes Verissimo',
    'email' => 'thiago.verissimo@usp.br',
  ],
];

$webform_submission = WebformSubmission::create($values);
$webform_submission->save();
```

### Exercício 3

Neste exercício vamos trabalhar com o seguinte arquivo:

[https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv](https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv)

- Criar um webform com as colunas desse arquivo
- Criar um arquivo php que leia o arquivo csv completo ([https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv](https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv)) e para cada linha crie um submissão correspondente no webform criado anteriormente (rodar seu script com drush)

## Dia 4 (em construção)

Carregando todas submissões de um webform:

```bash
use Drupal\webform\Entity\Webform;
use Drupal\webform\Entity\WebformSubmission;

$webform_id = 'meu_webform';
$webform = Webform::load($webform_id);

if ($webform->hasSubmissions()) {
  $query = \Drupal::entityQuery('webform_submission')->condition('webform_id', $webform_id );
  $result = $query->execute();
  $submission_data = [];
  foreach ($result as $item) {
    $submission = \Drupal\webform\Entity\WebformSubmission::load($item);
    $data = $submission->getData();
    ...
}
```

## Extras

trocar a url alternativa:

```bash
$node->path->alias = '/novo-caminho-do-node'
$node->path->pathauto = Drupal\pathauto\PathautoState::SKIP;
```

-->


# Workaround PHP 7.4

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




