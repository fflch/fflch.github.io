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

### Preparação do Ambiente

O primeiro passo é criar um diretório isolado.

```bash
mkdir cursodrupal
cd cursodrupal
```

O Drupal moderno é baseado em componentes PHP (Symfony) e gerenciado pelo Composer. O comando abaixo usa uma imagem oficial do Composer para baixar os arquivos do Drupal para sua máquina, sem que você precise instalar nada além do Docker.

```bash
docker run --rm -it \
  -v $(pwd):/app \
  -u $(id -u):$(id -g) \
  composer:latest \
  composer create-project drupal/recommended-project . --ignore-platform-reqs
```

Nosso Dockerfile está preparado para rodar no ambiente USP.

```bash
FROM php:8.4-apache

# packages
RUN sed -i 's|main|main non-free|' /etc/apt/sources.list.d/debian.sources && apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    freetds-bin \
    freetds-dev \
    libicu-dev \
    git \
    unzip \
    libzip-dev \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \ 
    curl

# cleanup
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# php libs
RUN docker-php-ext-install \
    intl \
    pdo_mysql \
    soap \
    zip \
    mbstring \
    bcmath \
    pdo_dblib

# gd
RUN docker-php-ext-configure gd --with-freetype --with-jpeg && \
    docker-php-ext-install gd

# php memory
ENV PHP_MEMORY_LIMIT=512M
ENV PHP_UPLOAD_LIMIT=512M
RUN { \
        echo 'memory_limit=${PHP_MEMORY_LIMIT}'; \
        echo 'upload_max_filesize=${PHP_UPLOAD_LIMIT}'; \
        echo 'post_max_size=${PHP_UPLOAD_LIMIT}'; \
    } > "${PHP_INI_DIR}/conf.d/upload.ini"

# apache
RUN a2enmod rewrite
RUN sed -i 's|/var/www/html|/var/www/html/web|' /etc/apache2/sites-available/000-default.conf
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# composer
WORKDIR /var/www/html

CMD ["apache2-foreground"]
```

o docker-compose.yml nos entrega o banco de dados (MariaDB) na mesma rede do nosso container principal.

```bash
services:
  cursodrupal:
    image: cursodrupal:latest
    container_name: cursodrupal
    ports:
      - "8000:80"
    depends_on:
      - mariadb
    networks:
      - cursodrupal-network
    volumes:
      - ./:/var/www/html
    environment:
      HOME: /tmp
    user: "${UID:-1000}:${GID:-1000}"

  mariadb:
    image: mariadb:11
    container_name: cursodrupal_mariadb
    restart: always
    environment:
      MYSQL_DATABASE: cursodrupal
      MYSQL_USER: cursodrupal
      MYSQL_PASSWORD: cursodrupal
      MYSQL_ROOT_PASSWORD: cursodrupal
    volumes:
      - mariadb_data:/var/lib/mysql
    networks:
      - cursodrupal-network

networks:
  cursodrupal-network:

volumes:
  mariadb_data:
```

Agora executamos o build da imagem e iniciamos o site.
```bash
docker build --no-cache -t cursodrupal .
docker compose up 
```

Acesse http://localhost:8000/

Instalação automática do Drupal

```bash
docker exec -it cursodrupal composer update

docker exec -it cursodrupal composer require drush/drush

docker exec -it cursodrupal ./vendor/bin/drush site:install standard \
  --db-url="mysql://cursodrupal:cursodrupal@mariadb/cursodrupal" \
  --site-name="Site Treinamento" \
  --account-name="admin" \
  --account-pass="admin" \
  --yes
```

Criando o Módulo Customizado: Gerador de CPF:
```bash
docker exec -it cursodrupal ./vendor/bin/drush generate module
```

Uma rota para mostrar os CPFs gerados:
```bash
docker exec -it cursodrupal ./vendor/bin/drush generate controller
```

Verificando os arquivos gerados:
```bash
cat web/modules/geracpf/geracpf.routing.yml
code web/modules/geracpf/src/Controller/GeracpfController.php
```

Em vez de reinventar a roda, instalamos uma biblioteca que já sabe como gerar CPFs válidos (https://github.com/LacusSolutions/br-utils-php_cpf-gen):

```bash
docker exec -u root -it cursodrupal composer require lacus/cpf-gen
```

No controller usar a biblioteca externa:
```bash
use Lacus\CpfGen\CpfGenerator;

$generator = new CpfGenerator();

// With options
$cpf = $generator->generate(
    format: true
); 
```
Sempre que você altera o código de rotas ou cria novos arquivos, o Drupal precisa ser avisado:
```bash
docker exec -it cursodrupal ./vendor/bin/drush cr
```
Mas podemos desligar o cache:

```bash
$build['content'] = [
  '#type' => 'item',
  '#markup' => $cpf,
  '#cache' => [
    'max-age' => 0,
  ],
];
```

### Exercício 1

Criar um módulo chamado geracnpj, que exiba um cnpj aleatório, assim como fizemos no geracpf. 

Criar um segundo módulo chamado gerafrases, que mostrará frases inspiradoras dependendo do dia da semana. As frases que deverão ser mostradas estão no arquivo csv [frases](/assets/files/frases.csv). Na próxima reunião, cada membro do grupo (estagiários e funcionários) deve apresentar os dois módulos na TV.

## Dia 2

CRUD para cadastro de frases. Nosso módulo se chamará `muralmotivacional`:

```bash
docker exec -it cursodrupal ./vendor/bin/drush generate module
```

Criando tabela no banco de dados em ```muralmotivacional/muralmotivacional.install```:

```php
<?php
function muralmotivacional_schema() {
  $schema['muralmotivacional'] = [
    'description' => 'Tabela de frases motivacionais',
    'fields' => [
      'id' => [
        'type' => 'serial',
        'not null' => TRUE,
      ],
      'frase' => [
        'type' => 'text',
        'not null' => TRUE,
      ],
      'dia' => [
        'type' => 'varchar',
        'length' => 50,
        'not null' => TRUE,
      ],
    ],
    'primary key' => ['id'],
  ];
  return $schema;
}
```

habilitar módulo:

```bash
docker exec -it cursodrupal ./vendor/bin/drush en muralmotivacional -y
```

Gerar formulário para cadastro de frases:

```bash
docker exec -it cursodrupal ./vendor/bin/drush generate form

Module name: muralmotivacional
Rota: /muralmotivacional/create
Class name: CreateFraseForm
Form ID: muralmotivacional_form
```

Método no `muralmotivacional/src/Form/CreateFraseForm.php`:

```php
<?php
use Drupal\Core\Database\Database;

public function buildForm(array $form, FormStateInterface $form_state) {
  $form['frase'] = [
    '#type' => 'textarea',
    '#title' => 'Frase',
    '#required' => TRUE,
  ];
  $form['dia'] = [
    '#type' => 'select',
    '#title' => 'Dia da semana',
    '#options' => [
      'Segunda-Feira' => 'Segunda-Feira',
      'Terça-Feira'   => 'Terça-Feira',
      'Quarta-Feira'  => 'Quarta-Feira',
      'Quinta-Feira'  => 'Quinta-Feira',
      'Sexta-Feira'   => 'Sexta-Feira',
    ],
  ];
  $form['actions']['submit'] = [
    '#type' => 'submit',
    '#value' => 'Salvar',
  ];
  return $form;
}

public function submitForm(array &$form, FormStateInterface $form_state) {
  $connection = Database::getConnection();
  $connection->insert('muralmotivacional')
    ->fields([
      'frase' => $form_state->getValue('frase'),
      'dia' => $form_state->getValue('dia'),
    ])
    ->execute();
  \Drupal::messenger()->addMessage('Frase salva com sucesso!');
}
```

Limpar cache e acessar formulário na rota `/muralmotivacional/create`:

```bash
docker exec -it cursodrupal ./vendor/bin/drush cr
```

Vamos criar um controler com as operações do CRUD `MuralMotivacionalController`,*sem rotas*:

```bash
docker exec -it cursodrupal ./vendor/bin/drush generate controller
```

Operações de CRUD no controller:

```php
use Drupal\Core\Database\Database;
public function index() {
    $connection = Database::getConnection();
    $query = $connection->select('muralmotivacional', 'm')->fields('m');
    $frases = $query->execute();
    $items = [];
    foreach ($frases as $frase) {
      $items[] = [
        '#markup' =>
          '<hr>
          <strong>Dia:</strong> ' . $frase->dia . '<br>
          <strong>Frase:</strong> ' . $frase->frase . '<br>
          <a href="/muralmotivacional/' . $frase->id . '/edit"> Editar </a> <br>
          <a href="/muralmotivacional/' . $frase->id . '/delete"> Apagar </a> '
      ];
    }
    return [
      '#cache' => [
        'max-age' => 0,
      ],
      'content' => $items,
    ];
}

public function delete($id) {
  $connection = Database::getConnection();
  $connection->delete('muralmotivacional')
    ->condition('id', $id)
    ->execute();
  \Drupal::messenger()->addMessage('Frase apagada com sucesso');
  return $this->redirect('muralmotivacional.index');
}
```

Rotas `muralmotivacional/muralmotivacional.routing.yml`:


```yml
muralmotivacional.index:
  path: '/muralmotivacional'
  defaults:
    _controller: '\Drupal\muralmotivacional\Controller\MuralMotivacionalController::index'
    _title: 'Lista de Frases'
  requirements:
    _permission: 'access content'

muralmotivacional.delete:
  path: '/muralmotivacional/{id}/delete'
  defaults:
    _controller: '\Drupal\muralmotivacional\Controller\MuralMotivacionalController::delete'
    _title: 'Apagar Frase'
  requirements:
    _permission: 'access content'
```

Formulário de edição `muralmotivacional/src/Form/EditFraseForm.php`:

```bash
docker exec -it cursodrupal ./vendor/bin/drush generate form
rota: /muralmotivacional/edit
```

Formulário de Edição

```php
use Drupal\Core\Database\Database;
public function buildForm(array $form, FormStateInterface $form_state, $id = NULL) {
  $connection = Database::getConnection();
  $query = $connection
    ->select('muralmotivacional', 'm')
    ->fields('m')
    ->condition('id', $id);
  $frase = $query->execute()->fetchObject();
  $form['id'] = [
    '#type' => 'hidden',
    '#value' => $frase->id,
  ];
  $form['frase'] = [
    '#type' => 'textarea',
    '#title' => 'Frase',
    '#required' => TRUE,
    '#default_value' => $frase->frase,
  ];
  $form['dia'] = [
    '#type' => 'select',
    '#title' => 'Dia da semana',
    '#options' => [
      'Segunda-Feira' => 'Segunda-Feira',
      'Terça-Feira'   => 'Terça-Feira',
      'Quarta-Feira'  => 'Quarta-Feira',
      'Quinta-Feira'  => 'Quinta-Feira',
      'Sexta-Feira'   => 'Sexta-Feira',
    ],
    '#default_value' => $frase->dia,
  ];
  $form['actions']['submit'] = [
    '#type' => 'submit',
    '#value' => 'Atualizar',
  ];
  return $form;
}

public function submitForm(array &$form, FormStateInterface $form_state) {
  $connection = Database::getConnection();
  $connection->update('muralmotivacional')
    ->fields([
      'frase' => $form_state->getValue('frase'),
      'dia' => $form_state->getValue('dia'),
    ])
    ->condition('id', $form_state->getValue('id'))
    ->execute();
  \Drupal::messenger()->addMessage('Frase atualizada com sucesso!');
}
```

Rota com parâmetro:

```bash
muralmotivacional.edit:
  path: '/muralmotivacional/{id}/edit'
  defaults:
    _form: '\Drupal\muralmotivacional\Form\EditFraseForm'
    _title: 'Editar Frase'
  requirements:
    _permission: 'access content'
```

### Exercício 2

Criar um módulo chamado livros e implementar as operações de CRUD para o livro com os campos título, autor e ano.

<!--


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

-->




