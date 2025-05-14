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

# 2 - Criando a primeira revista

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

<!---

## Criação de um plugin do tipo Block

O OJS, assim como outras plataformas, tem vários estilos de plugin. Na presente parte vamos explicar passo a passo a criar um plugin do estilo bloco.

Alguns plugins devem ser aplicado somente nas revistas, como por exemplo um plugin com a nuvem de palavras. Outros plugins devem ser aplicados de forma global, no site principal que cuida das revistas, como exemplo um plugin que exibe as estatísticas de revistas gerenciadas pelo site.

Na pasta plugins/blocks devemos criar uma pasta com o nome de nosso novo plugin. Façamos isso pelo seguinte código:

```bash
mkdir estatis
```

- Com isso, devemos adentrar a pasta que acabamos de criar e criar uma  outra pasta chamada templates. Façamos isso pelo seguinte código:

```bash
mkdir templates
```

- Após isso devemos criar os arquivos Index, NomePluginBlockPlugin.inc.php, o settings.xml e o version.xml. Façamos isso a partir dos seguintes códigos:

```bash
touch index.php
touch NomePluginBlockPlugin.php
touch version.xml
```

- Após a criação dos arquivos, devemos entrar na pagina templates e criar o arquivo block.tpl. Façamos isso atraves do código:

```bash
touch block.tpl
```

## 3.2 - Programando o Plugin

### 3.2.1 - Index.php

- O arquivo index.php é um carregador simples. Nele deve conter o código que instância a classe principal do seu plugin e retorna uma nova instância do mesmo plugin. Podemos ver um exemplo abaixo:

```php
 <?php

require_once('NomePluginBlockPlugin.php');

return new NomePluginBlockPlugin();

?>
```

### 3.2.2 - version.xml

- O version.xml somente é visto pelo instalador de plugins do OJS. Ele indica a versão do plugin e reconhece caso precise atualizar o plugin. O arquivo version.xml é importante porque, se você apenas colocar seus arquivos no diretório OJS, em vez de passar pelo instalador adequado, não haverá uma linha correspondente na tabela de plugins do banco de dados e você não poderá habilitar/desabilitar seu plugin.

- O "application" é o nome do plugin e "class" é a classe principal do plugin, conforme especificado no arquivo index.php. Podemos ver um exemplo abaixo:


```php
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE version SYSTEM "../../../lib/pkp/dtd/pluginVersion.dtd">
<version>
   <application>NomePlugin</application>
   <type>plugins.blocks</type>
   <release>1.0.0.0</release>
   <date>2023-01-06</date>
   <lazy-load>1</lazy-load>
   <class>NomePluginBlockPlugin</class>
</version>
```

### 3.2.3 - NomePluginBlockPlugin.php

- Então agora que nós temos uma estrutura básica, precisaremos criar o arquivo que o index.php está carregando, no meu caso chamado NomePluginBlockPlugin.php. Isso precisa ser desenvolvido com algumas funções iniciais: register, getDisplayName, getDescription, isSitePlugin e getContents. Podemos ver um exemplo abaixo:

```php
<?php
import('lib.pkp.classes.plugins.BlockPlugin');

class NomePluginBlockPlugin extends BlockPlugin {

	function getContextSpecificPluginSettingsFile() {
		return $this->getPluginPath();
	}

	public function register($category, $path, $mainContextId = NULL) {

    $success = parent::register($category, $path);

		if ($success && $this->getEnabled()) {
    }
		return $success;
	}

	public function getDisplayName() {
		return 'Plugin Exemplo';
	}

	public function getDescription() {
		return 'Esse é um plugin de exemplo';
	}


  public function isSitePlugin() {
    return true;
  }

  public function getContents($templateMgr, $request = null) {
    $ola = 'Olá Mundo!'

    //Exibição
    $templateMgr->assign('ola', $ola);
    return parent::getContents($templateMgr, $request);
  }
}
```

### 3.2.4 - block.tpl

- Por fim, o block.tpl é responsável pela exibição de nosso plugin. Assim, o que conter nele será exibido ao habilitarmos o plugin em nosso site.

```php
<div class="pkp_block">
    Texto: {$ola} 
</div>
```

## 3.3 - Como instalar o plugin na sua revistas

- Com o plugin terminado, devemos adentrar na área de administrador do OJS.

![Primeira parte](/assets/images/OJS/Instalacao_Plugin/Install1.png)

- Devemos clicar no lado superior esquerdo e selecionar a revista que em desejamos inserir o plugin.

![Segunda parte](/assets/images/OJS/Instalacao_Plugin/Install2.png)

- Após isso, devemos observar o lado esquerdo da tela e selecionar a opção Website, depois devemos entrar na subpartição plugins.

![Terceira parte](/assets/images/OJS/Instalacao_Plugin/Install3.png)

- Dentro da subpartição plugins, devemos encontrar o nosso plugin e ativá-lo.

![Quarta parte](/assets/images/OJS/Instalacao_Plugin/Install4.png)

- Após isso, devemos voltar a subpartição aparência e depois devemos escolher a opção configurar.

![Quinta parte](/assets/images/OJS/Instalacao_Plugin/Install5.png)

- Em configurar, devemos descer a tela e ativar o nosso plugin, após isso precisaremos apertar no nome de nossa revista no canto superior esquerdo.

![Sexta parte](/assets/images/OJS/Instalacao_Plugin/Install6.png)

- Pronto, seu plugin está visível em seu site.

![Setima parte](/assets/images/OJS/Instalacao_Plugin/Install7.png)

Escrito por Pedro Cesar Antunes de Amigo

- Foto do OJS clicavel.

[![Logo do OJS](/assets/images/OJS/ojs.png)](https://pkp.sfu.ca/)


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

