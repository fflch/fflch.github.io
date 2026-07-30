---
layout: default
title: Moodle
parent: Tutoriais
nav_order: 2
---
1. TOC
{:toc}
---

# Dia 1

## Instalação 

O Moodle é uma plataforma de aprendizado online, conhecida como LMS (Learning Management System), que permite criar, gerenciar e oferecer cursos e treinamentos pela internet. Ele é uma ferramenta de código aberto, o que significa que é gratuito e pode ser personalizado de acordo com as necessidades de cada instituição ou projeto. 

Antes de instalar o Moodle no Debian, é necessário garantir que todas as dependências estejam instaladas. O Moodle depende do PHP e de algumas extensões, além de um banco de dados como MariaDB. Aqui estão os principais pacotes que devem ser instalados no Debian:

```bash
sudo apt-get install php php-common php-cli php-gd php-curl php-xml php-mbstring php-zip php-sybase php-mysql php-intl
sudo apt-get install mariadb-server git
```
O Composer é um gerenciador de dependências para PHP. Ele permite instalar, atualizar e gerenciar bibliotecas e pacotes de forma simples, garantindo que um projeto tenha todas as dependências necessárias. Para instalação do composer:

```
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

Usaremos o Composer para instalar o Moodle e seus plugins:
```bash
git clone https://github.com/fflch/moodle4_composer.git
cd moodle4_composer
composer install
```

Além disso, é importante configurar o banco de dados, pois ele será usado para instalar o Moodle. Vamos inicialmente criar um usuário admin com senha admin e criar um banco de dados chamado *moodle*:

```bash
sudo mariadb
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%'  IDENTIFIED BY 'admin' WITH GRANT OPTION;
create database moodle;
quit
```

O comando a seguir é uma maneira rápida e simples de subir um servidor web embutido no PHP, sem a necessidade de configurar servidores complexos como Apache ou Nginx. Ele é especialmente útil durante o desenvolvimento, pois permite testar aplicações diretamente no ambiente local de forma ágil. 

```bash
php -S 0.0.0.0:8888 -t moodle -c php.ini
```
## Criação do plugin

Um plugin no Moodle é uma extensão que adiciona funcionalidades específicas à plataforma, permitindo personalizar e expandir suas capacidades. Ele pode ser usado para adicionar novos tipos de atividades, recursos, blocos, temas ou até mesmo integrações com ferramentas externas. Os plugins são desenvolvidos para se integrar ao Moodle de forma modular, sem alterar o núcleo do sistema, o que facilita a atualização e a manutenção.

Vamos criar um plugin básico do tipo bloco no Moodle chamado `livros`. Esse bloco vai simplesmente listar alguns livros.  No Moodle, os plugins do tipo bloco seguem uma estrutura de pastas e arquivos específica. Vamos criar a estrutura inicial para o nosso bloco.

```bash
cd blocks
mkdir livros
cd livros
```

Criar o Arquivo `version.php`, que define a versão do plugin e suas dependências:

```php
<?php
defined('MOODLE_INTERNAL') || die();

$plugin->component = 'block_livros';
$plugin->version = 2025010101;
```

O arquivo `block_livros.php` contém a lógica principal do bloco:

```php
<?php
defined('MOODLE_INTERNAL') || die();

class block_livros extends block_base {
    public function init() {
        $this->title = 'Livros'; 
    }
	
    public function get_content() {        
        $livros = [
            'Memórias de um Sargento de Milícias',
            'O Primo Basílio',
            'Memórias Póstumas de Brás Cubas',
            'A Hora da Estrela',
        ];	
        $this->content = new stdClass;
        $this->content->text = '<ul>';
        foreach ($livros as $livro) {
            $this->content->text .= '<li>' . $livro . '</li>';
        }
        $this->content->text .= '</ul>';
        return $this->content;
    }
}
```

A pasta lang de um plugin no Moodle é responsável por armazenar os arquivos de idioma do plugin. Esses arquivos contêm todas as strings de texto que o plugin utiliza, permitindo que ele seja traduzido para diferentes idiomas. O arquivo  `pluginname.php`retorna um array associativo com as chaves e valores das mensagens/textos.

```bash
mkdir -p lang/en
mkdir -p lang/pt_br
```

Versão em português `lang/pt_br/block_livros.php`:

```php
<?php
defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'Livros'; 
```

Versão em inglês `lang/en/block_livros.php`:

```php
<?php
defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'Books';
```

Por fim, podemos podemos ativar nosso plugin pela interface ou com o comando:

```bash
php admin/cli/upgrade.php
```

Com o intuito de deixar nosso plugin em multi-idiomas, ainda na pasta lang, no array `$string` podemos criar novas chaves, por exemplo, `$string['title']='Título';` em ambas as pastas, `en` e `pt-br` e usar na nossa classe a chamada `get_string('title', 'block_livros');` ao invés de usar strings de texto diretamente no código php.

## Templates

Os arquivos Mustaches são um template de interface HTML que separa o conteúdo (dados) da apresentação (visual). São usados para gerar a interface do usuário de forma limpa e organizada, com suporte a variáveis, condicionais e laços de repetição, sem conter lógica PHP diretamente.

```bash
mkdir templates
```
A nova implementação do método `get_content` usando templates será:
```php
public function get_content() {        
    $livros = [
        'Memórias de um Sargento de Milícias',
        'O Primo Basílio',
        'Memórias Póstumas de Brás Cubas',
        'A Hora da Estrela',
    ];	
    $this->content = new stdClass;
    $this->content->text = $this->render_from_template('block_livros/livros', $livros);
    return $this->content;
}
```

E por fim, o arquivo mustache `templates/livros.mustache`:
```html
<ul>
  {{#livros}}
    <li>{{titulo}}</li>
  {{/livros}}
</ul>
```


{{#str}} nome_da_string, nome_do_plugin {{/str}}

 
## Exercício 1 - Importação de Dados e Estatísticas no bloco do Moodle

**Objetivo**: Criar um plugin no Moodle para ler dados de um arquivo CSV e exibir estatísticas desses dados em um bloco.

[https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv](https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv)

- Ler o arquivo `exercise.csv` dentro do método `get_content()` do bloco.
- Calcular a média da coluna pulse para cada tipo de atividade (rest, walking, running).
- Exibir a tabela abaixo no bloco com as informações lidas e processadas do csv.

|  exercise.csv| rest  | walking   | running |
|--------------|-------|-----------|---------|
|  Qtde linhas |  XX   |     XX    |   XXX   | 
|  Média Pulse |  XX   |     XX    |   XXX   |

# Dia 2

CRUD é um acrônimo para as quatro operações básicas utilizadas na manipulação de dados em sistemas web: Create (Criar), Read (Ler), Update (Atualizar) e Delete (Excluir). Essas operações interagem com bancos de dados, permitindo, por exemplo, que usuários possam cadastrar novas informações, visualizar registros existentes, modificar dados já salvos e remover registros.

Vamos criar um CRUD para cadastro de livros com os seguintes campos: título, autor e isbn.

Suponha que sua versão atual seja 2025040805. Você precisa incrementar esse número:

```php
$plugin->version = 2025040806;
```

O banco de dados pode ser alterado usando o arquivo `db/upgrade.php`:

```php
<?php

defined('MOODLE_INTERNAL') || die();

function xmldb_block_estagiarios_upgrade($oldversion) {
    global $DB;

    $dbman = $DB->get_manager();

    if ($oldversion < 2025011403) {
        $table = new xmldb_table('estagiarios_livros');

        $table->add_field('id', XMLDB_TYPE_INTEGER, '10', null, XMLDB_NOTNULL, XMLDB_SEQUENCE, null);
        $table->add_field('titulo', XMLDB_TYPE_CHAR, '255', null, XMLDB_NOTNULL, null, null);
        $table->add_field('autor', XMLDB_TYPE_CHAR, '255', null, XMLDB_NOTNULL, null, null);
        $table->add_field('isbn', XMLDB_TYPE_CHAR, '13', null, XMLDB_NOTNULL, null, null);

        $table->add_key('primary', XMLDB_KEY_PRIMARY, ['id']);

        if (!$dbman->table_exists($table)) {
            $dbman->create_table($table);
        }

        // Marca upgrade completo
        upgrade_plugin_savepoint(true, 2025011403, 'block', 'estagiarios');
    }

    return true;
}
```

Depois de aplicar a mudança verifique se a tabela foi criada no banco de dados com `desc mdl_estagiarios_livros`.

## Create

Vamos criar um formulário html para cadastro de livros que deverá ser um arquivo na pasta templates do tipo mustache (`templates/livros/create.mustache`):

```html
{% raw %}
<form method="post">
    <input type="hidden" name="sesskey" value="{{sesskey}}">
    <div>
        <label for="titulo">Título:</label>
        <input type="text" name="titulo" id="titulo"  required>
    </div>

    <div>
        <label for="autor">Autor:</label>
        <input type="text" name="autor" id="autor" required>
    </div>

    <div>
        <label for="isbn">ISBN:</label>
        <input type="text" name="isbn" id="isbn" required>
    </div>

    <button type="submit">Salvar</button>
</form>
{% endraw %}
```

A página de criação do arquivo pode ficar no caminho livros/create.php:

```php
<?php

require('../../../config.php');
require_login();

global $DB;

$PAGE->set_url(new moodle_url('/blocks/estagiarios/livros/create.php'));
$PAGE->set_context(context_system::instance());

// Renderiza o template
echo $OUTPUT->header();

echo $OUTPUT->render_from_template('block_estagiarios/livros/create', [
    'sesskey' => sesskey()
]);

echo $OUTPUT->footer();
```

Para salvar após a submissão do formulário podemos fazer:

```php
// Processamento do form (se submetido)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && confirm_sesskey()) {
    $livro = new stdClass();
    $livro->titulo = optional_param('titulo', '', PARAM_TEXT);
    $livro->autor = optional_param('autor', '', PARAM_TEXT);
    $livro->isbn = optional_param('isbn', '', PARAM_TEXT);

    $DB->insert_record('estagiarios_livros', $livro);
    redirect('create.php', 'Livro salvo com sucesso!');
}
```
Vamos criar um template para listar os livros em uma tabela (`templates/livros/index.mustache`):

```html
{% raw %}
<h2>Livros cadastrados</h2>

<a href="create.php"> Cadastrar Livro </a>

<table class="generaltable">
    <thead>
        <tr>
            <th>Título</th>
            <th>Autor</th>
            <th>ISBN</th>
        </tr>
    </thead>
    <tbody>
        {{#livros}}
        <tr>
            <td>{{titulo}}</td>
            <td>{{autor}}</td>
            <td>{{isbn}}</td>
        </tr>
        {{/livros}}
    </tbody>
</table>
{% endraw %}
```
E por fim a página index:

```php
<?php

require('../../../config.php');
require_login();

global $DB;

$PAGE->set_url(new moodle_url('/blocks/estagiarios/livros/index.php'));
$PAGE->set_context(context_system::instance());

$livros = $DB->get_records('estagiarios_livros');

echo $OUTPUT->header();

$livros = $DB->get_records('estagiarios_livros');
$livros = array_values($livros);

echo $OUTPUT->render_from_template('block_estagiarios/livros/index', [
    'livros' => $livros,
]);

echo $OUTPUT->footer();
```

## Exercício 2

1. Criar uma tabela no plugin com todos os campos dos livros: [https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv](https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv)
2. Criar uma página de importação em `livros/import.php`. Ler o arquivo csv conforme feito no exercício 1, e importar o csv: [https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv](https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv) (esse é o completo!)
3. Criar as seguintes páginas: 

    - `livros/by_year.php`: uma tabela com a quantidade de livros por ano
    - `livros/by_author.php`: uma tabela com a quantidade de livros por autor
    - `livros/by_language.php`: uma tabela com a quantidade de livros por idioma
4. Criar um formulário de cadastro para inserção manual de livro com os campos [https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv](https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv)

# Dia 3

No Moodle, embora seja tecnicamente possível criar formulários diretamente em HTML puro, como fizemos na seção anterior, a utilização da API de formulários é a abordagem recomendada. O principal motivo é que o moodleform já oferece, de maneira integrada e automática, uma série de recursos fundamentais para segurança, validação, usabilidade e consistência visual.

Ao utilizar a API de formulários, o desenvolvedor não precisa se preocupar em implementar do zero validações básicas como campos obrigatórios, tipos de dados esperados (texto, inteiro, e-mail, etc.) ou validações personalizadas. O moodleform cuida de tudo isso de forma padronizada, incluindo também a proteção contra ataques CSRF (Cross-Site Request Forgery) por meio do sesskey, que é automaticamente gerado e validado pela plataforma. Além disso, o Moodle oferece suporte integrado a mensagens de erro amigáveis, multilíngues e associadas diretamente aos campos do formulário, melhorando a experiência do usuário e garantindo acessibilidade.

Os formulários criados com a API do Moodle seguem o padrão visual e estrutural da interface da plataforma, adaptando-se automaticamente ao tema ativo. Também facilita a manutenção e a reutilização, uma vez que o formulário é encapsulado em uma classe própria, podendo ser utilizado em diferentes pontos do sistema, como páginas de adição, edição ou exclusão de registros, sem duplicação de código.

Um exemplo de formulário, com os dois campos, título e tipo da capa. Vamos chamar esse arquivo de `livros_form.php`:

```php
<?php
require_once("$CFG->libdir/formslib.php");
class livros_form extends moodleform {
    public function definition() {
        $this->_form->addElement('text', 'titulo', 'Título');
        $this->_form->addElement('select', 'tipo_capa', 'Tipo da capa do livro', ['normal', 'dura']);
        $this->_form->addElement('submit', 'button', 'Enviar');
        
        $this->_form->addRule('titulo', null, 'required');
        $this->_form->addRule('titulo', null, 'required');
        $this->_form->addRule('tipo_capa', null, 'required');
    }
```

Para chamarmos esse formulário em uma `view` e o mandarmos como parâmetro para o mustache, fazemos:

```php
<?php
require_once('livros_form.php');
$livros_form = new livros_form();

$data = [
    ...
    'livros_form' => $livros_form->render(),
    ...
];
```

No mustache basta mostrar o formulário com `{% raw %}{{{ livros_form }}}{% endraw %}`.


Para receber a requisição com os dados preenchidos do formulário:

```php
<?php
global $DB;

$request = $uploadform->get_data();
if(!empty($request) and !is_null($request)){

    $livro = new stdClass();
    $livro->titulo =$request->titulo;
    $livro->tipo_capa = $request->tipo_capa;
    DB->insert_record('estagiarios_livros', $livro);
    redirect('create.php', 'Livro salvo com sucesso!');
}
```

## Exercício 3

1. Mudar o formulário do exercício 2 para usar o form API do Moodle e não o formulário html diretamente.
2. No exercício 2 fizemos a importação do arquivo csv fixando esse arquivo dentro do código php. Agora, criar um formulário de importação de livros no qual o usuário fará upload do arquivo csv. O trecho de código abaixo pode ajudar:

```php
# 1. no form api:
    $this->_form->addElement('file', 'arquivocsv', 'arquivo csv');

# 2. Na leitura do request:
    $conteudo_do_csv = $uploadform->get_file_content('arquivocsv');
```

