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

# Dia 1

## Preparação do Ambiente

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

## Exercício 1

Criar um módulo chamado geracnpj, que exiba um cnpj aleatório, assim como fizemos no geracpf. 

Criar um segundo módulo chamado gerafrases, que mostrará frases inspiradoras dependendo do dia da semana. As frases que deverão ser mostradas estão no arquivo csv [frases](/assets/files/frases.csv). Na próxima reunião, cada membro do grupo (estagiários e funcionários) deve apresentar os dois módulos na TV.

# Dia 2

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

## Exercício 2

Criar um módulo chamado livros e implementar as operações de CRUD para o livro com os campos título, autor e ano.


# Dia 3

Adaptação do Dockerfile conforme: [https://github.com/uspdev/dockerfiles/blob/master/php-apache/readme.md](https://github.com/uspdev/dockerfiles/blob/master/php-apache/readme.md)


O módulo Webform do Drupal serve para criar e gerenciar formulários no site sem precisar programar tudo manualmente. Ele é um dos módulos mais usados do na FFLCH.

```bash
docker exec -it cursodrupal composer require 'drupal/webform:^6.3@beta'
```

Um plugin é um mecanismo de extensibilidade que permite definir comportamentos intercambiáveis e reutilizáveis dentro de um módulo. Vamos criar um campo no webform chamado email USP e o módulo chamaremos de USP:

```bash
docker exec -it cursodrupal ./vendor/bin/drush generate module

usp/
└── src/
    ├── Element/
    │   └── EmailUspElement.php        -> Form API (editor, validação)
    └── Plugin/
        └── WebformElement/
            └── EmailUspElement.php    -> Webform Plugin - Configurações
```

`src/Element/EmailUspElement.php` teremos:

```php
<?php

namespace Drupal\usp\Element;

use Drupal\Core\Form\FormStateInterface;
use Drupal\Core\Render\Element\Textfield;

/**
 * Provides a USP email element.
 *
 * @FormElement("email_usp")
 */
class EmailUspElement extends Textfield {

  public function getInfo(): array {
    $class = get_class($this);
    return parent::getInfo() + [
      '#input' => TRUE,
      '#element_validate' => [
        [$class, 'validateEmailUsp'],
      ],
    ];
  }

  public static function validateEmailUsp(&$element, FormStateInterface $form_state, &$complete_form): void {
    $value = trim($element['#value']);
    if (!str_contains($value, '@usp.br')) {
      $form_state->setError(
        $element,
        t('O valor informado deve conter @usp.br')
      );
    }
  }

}
```

E a Implementação do Plugin em `src/Plugin/WebformElement/EmailUspElement.php`:

```php
<?php

namespace Drupal\usp\Plugin\WebformElement;

use Drupal\webform\Plugin\WebformElement\TextField;

/**
 * Provides a 'email_usp' Webform element.
 *
 * @WebformElement(
 *   id = "email_usp",
 *   label = @Translation("E-mail USP"),
 *   description = @Translation("Campo personalizado USP."),
 *   category = @Translation("USP")
 * )
 */
class EmailUspElement extends TextField {
}
```

Vamos criar uma área para configuração do módulo, que diferente do CRUD, a responsabilidade de salvar os dados será do Drupal:

```bash
docker exec -it cursodrupal ./vendor/bin/drush  generate form:config

rota: /admin/config/usp/settings
```

Item no menu de configurações:

```php
usp.settings:
  title: 'USP'
  description: 'Configurações do módulo USP'
  parent: system.admin_config_system
  route_name: usp.settings
  weight: 10
```

Campo no formulário:

```php
$form['emails_proibidos'] = [
  '#type' => 'textarea',
  '#title' => $this->t('Emails proibidos'),
  '#description' => $this->t('Emails proibidos separados por virgula'),
  '#default_value' => $this->config('usp.settings')->get('emails_proibidos'),
];

// salvando
$this->config('usp.settings')
    ->set('emails_proibidos', $form_state->getValue('emails_proibidos'))
    ->save();
```

Voltando ao nosso plugin, podemos fazer uma segunda validação que verifica se o email não está proibido:


```php
$config = \Drupal::config('usp.settings');
$emails_proibidos = $config->get('emails_proibidos');
$emails_proibidos = explode(',', $emails_proibidos);
if (in_array($value, $emails_proibidos)) {
  $form_state->setError(
    $element,
    t('Email proibido. Por favor, informe um email diferente.')
  );
}
```

## Exercício 3

Criar um módulo chamado meuscampos e implementar os campos: Telefone Fixo em de São Paulo, Telefone celular em São Paulo, cpf e cnpj.