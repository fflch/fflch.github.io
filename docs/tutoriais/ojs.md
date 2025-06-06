---
layout: default
title: OJS
parent: Tutoriais
nav_order: 5
---
1. TOC
{:toc}
---

# Dia 1

## Instalação

O Open Journal Systems (OJS) é uma plataforma de código aberto desenvolvida pelo Public Knowledge Project (PKP) que permite a gestão e publicação de periódicos científicos online. Ele oferece ferramentas para todo o fluxo editorial, desde a submissão de artigos, avaliação por pares, edição e publicação, até a indexação e visibilidade dos conteúdos.

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
create database ojs3;
quit
```

Instalação do OJS. Escolher uma versão em (https://pkp.sfu.ca/software/ojs/download/)[https://pkp.sfu.ca/software/ojs/download/] e baixá-la.
```bash
wget https://pkp.sfu.ca/ojs/download/ojs-3.4.0-8.tar.gz
tar -vzxf ojs-3.4.0-8.tar.gz
cd ojs-3.4.0-8
php -S 0.0.0.0:8888
```

A configuração do OJS é bem intutiva, porém, ainda assim se complica em certos momentos. Assim, se faz necessário que tenhamos um passo a passo de como configurá-lo. Na primeira parte devemos escolher um nome de usuário e uma senha, além de fornecer um email para cadastro. Como estamos em um ambiente de programação e não de editorial de revista, podemos colocar usuário e senha como "admin" e o email como "admin@usp.br" como podemos observar na imagem.

![Primeira parte](/assets/images/OJS/Instalacao_OJS/Primera_Parte.png)

Na segunda parte devemos escolher a língua primária do OJS e as línguas adicionais do mesmo.

![Segunda parte](/assets/images/OJS/Instalacao_OJS/Segunda_Parte.png)

Na terceira parte devemos verificar se o local onde o diretório será criado é o qual desejamos.

![Terceira parte](/assets/images/OJS/Instalacao_OJS/Terceira_Parte.png)

Na quarta parte devemos:

- Trocar o banco de dados para MySQLi
- Adicionar o username que criamos no mariadb (no caso admin)
- Adicionar a senha que criamos no mariadb (no caso admin)
- Adicionar o nome da database que criamos no mariadb (no caso ojs3)

![Quarta parte](/assets/images/OJS/Instalacao_OJS/Quarta_Parte.png)

Com isso, só precisaremos confirmar as configurações e o seu OJS estará configurado.

## Criando a primeira revista

Assim que terminarmos a configuração do OJS, devemos criar a nossa primeira revista. Para isso, devemos entrar na área de administrador do OJS.

![Primeira parte](/assets/images/OJS/Instalacao_Plugin/Install1.png)

Após isso devemos clicar em `Revistas hospedadas`.

![Segunda parte](/assets/images/OJS/Cria_Revista/Parte1.png)

Agora devemos clicar em `criar revista`.

![Terceira parte](/assets/images/OJS/Cria_Revista/Parte2.png)

Agora devemos:

1. Escolher o nome de nossa revista;
1. Escolher a sigla de nossa revista;
1. Escolher a abreviatura de nossa revista (recomendada ser a mesma da sigla);
1. Escrever uma descrição para nossa revista;
1. Adicionar o final do caminho da revista (recomendado ser a mesma da sigla);
1. Escolher os idiomas que a revista terá e o idioma principal da mesma;
1. Permitir Acesso Livre a esta revista no portal;
1. Por fim, somente falta salvar a nossa revista e pronto.

![Quarta parte](/assets/images/OJS/Cria_Revista/Parte3.png)

![Quinta parte](/assets/images/OJS/Cria_Revista/Parte4.png)

Agora podemos observar que nossa revista foi criada.

![Sexta parte](/assets/images/OJS/Cria_Revista/Parte5.png)

## Exercício 1

Como administrador, crie 10 revistas fictícias no OJS, preenchendo as informações mínimas (nome, descrição, idioma). Em seguida, acesse cada revista como autor e submeta 2 artigos utilizando o fluxo editorial completo, passando por todas as etapas: submissão, designação de avaliadores, decisão editorial, edição, produção e publicação. Após isso, utilize a opção de submissão rápida e submeta 1 artigo por revista, publicando-o diretamente. Ao final, cada revista deverá conter 3 artigos publicados: 2 pelo fluxo completo e 1 pela submissão rápida.

# Dia 2

## Criação de um plugin do tipo Block

No OJS, assim como em outras plataformas, há vários tipos de plugins. Na presente parte vamos explicar o passo a passo para criarmos um plugin do tipo bloco. Na pasta plugins/blocks devemos criar uma pasta com o nome de nosso novo plugin: `mkdir estagiarios`. Dentro da pasta do nosso plugin, vamos criar alguns arquivos:


```bash
touch index.php
touch EstagiariosBlockPlugin.php
touch version.xml
mkdir templates
touch templates/block.tpl
```

O conteúdo do arquivo index.php deve retornar a instância da classe principal do plugin:
```php
<?php
return new \APP\plugins\blocks\estagiarios\EstagiariosBlockPlugin();
```

Já no arquivo xml há metadados do plugin:

```xml
{% raw %}
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE version SYSTEM "../../../lib/pkp/dtd/pluginVersion.dtd">

<version>
        <application>estagiarios</application>
        <type>plugins.blocks</type>
        <release>1.0.0.0</release>
        <date>2025-01-01</date>
        <lazy-load>1</lazy-load>
        <class>EstagiariosBlockPlugin</class>
</version>
{% endraw %}
```

O arquivo `block.tpl` será o arquivo renderizado com o conteúdo que vamos apresentar, no nosso plugin as lista de estagiários de TI da FFLCH-USP:
```html
{% raw %}
<h2>Estagiários(as) de TI da FFLCH-USP</h2>
<ul>
  <li>Maria</li>
  <li>João</li>
</ul>
{% endraw %}
```

Por fim, vamos definir nossa class `EstagiariosBlockPlugin.php` que deve conter no mínimos os métodos: getDisplayName, getDescription e getContents:

```php
<?php

namespace APP\plugins\blocks\estagiarios;

use PKP\plugins\BlockPlugin;

class EstagiariosBlockPlugin extends BlockPlugin {

	public function getDisplayName() {
		return 'Plugin dos Estagiários';
	}

    public function getDescription() {
		return 'Lista de estagiários de TI da FFLCH-USP';
	}

    public function getContents($templateMgr, $request = null) {
        return parent::getContents($templateMgr, $request);
    }

    public function isSitePlugin() {
        return true;
    }
}
```

Alguns plugins devem ser aplicado somente nas revistas, outros plugins devem ser aplicados de forma global, no site principal que cuida das revistas, como implementamos o método `isSitePlugin`, nosso bloco estará disponível em todo portal e não apenas em uma revista específica.


## Instalando o plugin

Na área de `Configurações do Portal` do OJS, acesse a aba plugins e habilite o plugin:

![Terceira parte](/assets/images/OJS/Instalacao_Plugin/Install3.png)

Após isso, limpe o cache e vá em aparência na opção configurar:

![Quinta parte](/assets/images/OJS/Instalacao_Plugin/Install5.png)

Em seguida, selecionar o plugin para aparecer na barra lateral:

![Sexta parte](/assets/images/OJS/Instalacao_Plugin/Install6.png)

Pronto, seu plugin está visível em seu site.

E se quisermos passarmos um array com a lista de estagiários da classe php para o template?

```php
<?php
    $estagiarios = ['maria','pedro', 'joão'];
    $templateMgr->assign('estagiarios', $estagiarios);
```
E no template block.tpl:

```html
{% raw %}
<ul>
    {foreach from=$estagiarios item=estagiario}
        <li>{$estagiario}</li>
    {/foreach}
</ul>
{% endraw %}
```

## Exercício 1 - Importação de Dados e Estatísticas no bloco do OJS

**Objetivo**: Criar um novo plugin no OJS para ler dados de um arquivo CSV e exibir estatísticas desses dados em um bloco.

[https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv](https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv)

- Ler o arquivo `exercise.csv` dentro do método `getContents()` do bloco.
- Calcular a média da coluna pulse para cada tipo de atividade (rest, walking, running).
- Exibir a tabela abaixo no bloco com as informações lidas e processadas do csv.

|  exercise.csv| rest  | walking   | running |
|--------------|-------|-----------|---------|
|  Qtde linhas |  XX   |     XX    |   XXX   | 
|  Média Pulse |  XX   |     XX    |   XXX   |


<!--
## 4 - sql

## 4.1 - sql puro

```php
import('lib.pkp.classes.db.DAO');

$dao = new DAO(); // Generic DAO
$result = $dao->retrieve(
    'SELECT s.submission_id, j.path AS journal_path, s.status 
     FROM submissions s 
     JOIN journals j ON s.context_id = j.journal_id
     WHERE s.status = ?',
    [STATUS_PUBLISHED]
);

// Process results
while (!$result->EOF) {
    $row = $result->GetRowAssoc(false);
    error_log(print_r($row, true));
    $result->MoveNext();
}
$result->Close();
```

## 4.2 - Registrando um DAO Data Access Object

Importante para reusabilidade plugins/generic/myPlugin/MyCustomDAO.inc.php:

```php
import('lib.pkp.classes.db.DAO');

class MyCustomDAO extends DAO {
    public function getSubmissionsWithAuthors() {
        $result = $this->retrieve(
            'SELECT s.submission_id, s.status, u.first_name, u.last_name 
             FROM submissions s 
             JOIN authors a ON s.submission_id = a.submission_id
             JOIN users u ON a.user_id = u.user_id'
        );

        $data = [];
        while (!$result->EOF) {
            $data[] = $result->GetRowAssoc(false);
            $result->MoveNext();
        }
        $result->Close();
        return $data;
    }
}
```

Usando o DAO acima em outras partes do plugin:

```php
$myDao = new MyCustomDAO();
$data = $myDao->getSubmissionsWithAuthors();
var_dump($data);
```

Listando todos DAOs disponíveis:

```php
$daoRegistry = DAORegistry::getAllDAOs(); // Get all registered DAOs

foreach ($daoRegistry as $daoName => $daoInstance) {
    echo("DAO Name: " . $daoName); // Log to PHP error log
}
```

Ou vendo as queries:

```bash
grep -r "class .*DAO" lib/classes
```

Por fim, alguns DAOs úteis:

<table>
    <tr>
        <th>DAO Name</th>
        <th>Purpose</th>
        <th>How to Access</th>
    </tr>
    <tr>
        <td>SubmissionDAO</td>
        <td>Handles submissions (articles)</td>
        <td><code>DAORegistry::getDAO('SubmissionDAO')</code></td>
    </tr>
    <tr>
        <td>UserDAO</td>
        <td>Manages user accounts</td>
        <td><code>DAORegistry::getDAO('UserDAO')</code></td>
    </tr>
    <tr>
        <td>JournalDAO</td>
        <td>Manages journals</td>
        <td><code>DAORegistry::getDAO('JournalDAO')</code></td>
    </tr>
    <tr>
        <td>IssueDAO</td>
        <td>Handles issues (journal editions)</td>
        <td><code>DAORegistry::getDAO('IssueDAO')</code></td>
    </tr>
    <tr>
        <td>SectionDAO</td>
        <td>Handles journal sections</td>
        <td><code>DAORegistry::getDAO('SectionDAO')</code></td>
    </tr>
    <tr>
        <td>ArticleGalleyDAO</td>
        <td>Manages article galleys (PDF, HTML formats)</td>
        <td><code>DAORegistry::getDAO('ArticleGalleyDAO')</code></td>
    </tr>
    <tr>
        <td>ReviewAssignmentDAO</td>
        <td>Handles review assignments</td>
        <td><code>DAORegistry::getDAO('ReviewAssignmentDAO')</code></td>
    </tr>
</table>


Exemplo usando o DAO UserDAO para listar todos usuários:


```php
$userDao = DAORegistry::getDAO('UserDAO'); 
$users = $userDao->getAll();

while ($user = $users->next()) {
    echo "User: " . $user->getFullName() . "<br>";
}
```

Para saber os métodos de um objeto:

```php
$userDao = DAORegistry::getDAO('UserDAO');
$methods = get_class_methods($userDao);

echo '<pre>';
print_r($methods);
echo '</pre>';
```


if you need detailed information (parameters, visibility, etc.), use ReflectionClass:

```php
$reflection = new ReflectionClass($user);
$methods = $reflection->getMethods();

echo '<pre>';
print_r($methods);
echo '</pre>';
```

--->

