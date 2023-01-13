---
layout: default
title: OJS
parent: Tutoriais
nav_order: 5
---
1. TOC
{:toc}
---

Escrito por Pedro Cesar Antunes de Amigo

# 0 - Preparação da infraestrutura de desenvolvimento do OJS

Instalação dos componentes básicos para desenvolvermos o OJS usando Debian e derivados. Verifique o procedimento correspondente para o seu sistema operacional.

## 0.0 - Instalar o Terminator

- Opcionalmente você pode instalar o Terminator, um terminal mais dinâmico. 

```bash
sudo apt install terminator
```

## 0.1 - Instalando o PHP para uso do OJS

- O PHP é essencial para o funcionamento do OJS, sendo ele também a linguagem a ser utilizada para a programação dos plugins

```bash
sudo apt install php php-intl php-mysql php-gd php-xml php-mbstring php-zip php-curl
```

## 0.2 - Instalando e configurando o git

- O git é de extrema necessidade para o meio de trabalho cooperativo, nele você poderá compartilhar o seus projetos.

```bash
sudo apt install git
git config --global user.name "Seu user cadastrado no GitHub"
git config --global user.email "Seu email cadastrado no GitHub"
```
Criar conta no GitHub e adicionar a chave pública gerada desta forma:

```bash
ssh-keygen
cat ~/.ssh/id_rsa.pub
```

## 0.3 - Instalar e configurar o banco de dados MariaDB

- O OJS requere do usuário um banco de dados, o MariaDB é um dos melhores do mercado e de fácil compreensão e utilização pelo usuário.

```bash
sudo apt install mariadb-server
sudo mariadb
```
```sql
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%'  IDENTIFIED BY 'admin' WITH GRANT OPTION;
quit
```

## 0.4 - Instalando o Visual Studio Code

- O Visual Studio Code é uma das ferramentas mais utilizadas para se criar e editar códigos. Sua instalação é opcional, mas é de extrema ajuda ao programar.

- Para baixarmos o Visual Studio Code deveremos clicar na imagem abaixo:

<div align="center">
<a href="https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64"><img src="/assets/images/OJS/VsCode.png" width="180" height="80"></a>
</div>

- Logo após baixarmos o arquivo, devemos executar o código abaixo e pronto, o Visual Studio Code estará funcionando perfeitamente.

```bash
sudo apt install ./ARQUIVO_BAIXADO.deb
```

## 0.5 - Baixando e instalando o Composer

- O Composer é uma ferramenta para gerenciamento de dependências em PHP. 

```bash
sudo apt install curl
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

## 0.6 - Baixando e instalando o OJS

- O OJS é a ferramenta de gerenciamento de revistas utilizado na USP. A versão que devemos utilizar é a versão 3.3.0-13.

- Primeiramente devemos baixar o OJS por meio do seguinte código: 

```bash
wget https://pkp.sfu.ca/ojs/download/ojs-3.3.0-13.tar.gz
```

- Após isso, devemos descompactar o OJS por meio do código:

```bash
tar -vzxf ojs-3.3.0-13.tar.gz
```

- Com isso, o OJS estará funcionando perfeitamente em sua máquina.

## 0.7 - Configurando o MariaDB para o OJS

- O MariaDB vem com alguns bancos de dados definidos, para utilizarmos o OJS devemos criar um banco de dados dedicado somente à ele.

```bash
mariadb -uadmin -padmin
```
```sql
Create database ojs3;
quit
```

## 0.8 - Iniciando o OJS

- Para a inicialização do OJS é preciso que estejamos na pasta em que ele esta instalado. Já na pasta, devemos inicializar o OJS pelo seguinte código:

```bash
php -S 0.0.0.0:8888
```

# 1 - Como configurar o OJS

A configuração do OJS é bem intutiva, porém, ainda assim se complica em certos momentos. Assim, se faz necessário que tenhamos um passo a passo de como configurá-lo em nossa máquina.

## 1.1 - Configuração

Para melhor entendimento, trabalharemos essa parte de forma visual.

Ao inicializar o OJS pela primeira vez, iremos configurá-lo para nos atender.

- Na primeira parte devemos escolher um nome de usuário e uma senha, além de fornecer um email para cadastro. Como estamos em um ambiente de programação e não de editorial de revista, podemos colocar usuário e senha como "admin" e o email como "admin@usp.br" como podemos observar na imagem.

![Primeira parte](/assets/images/OJS/Instalacao_OJS/Primera_Parte.png)

- Na segunda parte devemos escolher a língua primária do OJS e as línguas adicionais do mesmo.

![Segunda parte](/assets/images/OJS/Instalacao_OJS/Segunda_Parte.png)

- Na terceira parte devemos verificar se o local onde o diretório será criado é o qual desejamos.

![Terceira parte](/assets/images/OJS/Instalacao_OJS/Terceira_Parte.png)

- Na quarta parte devemos:

1. Trocar o banco de dados para MySQLi
1. Adicionar o username que criamos no mariadb (no caso admin)
1. Adicionar a senha que criamos no mariadb (no caso admin)
1. Adicionar o nome da database que criamos no mariadb (no caso ojs3)

![Quarta parte](/assets/images/OJS/Instalacao_OJS/Quarta_Parte.png)

- Com isso, só precisaremos confirmar as configurações e o seu OJS estará configurado.

# 2 - Criar um plugin do tipo Block

- O OJS, assim como outras plataformas, tem vários estilos de plugin. Na presente parte vamos explicar passo a passo a criar um plugin do estilo bloco.

## 2.0 - Identificando o estilo de Plugin

- Para começarmos a pensar sobre o plugin, devemos identificar o contexto que ele será aplicado. Como podemos ver abaixo:

1. Alguns plugins devem ser aplicado somente nas revistas, como por exemplo um plugin com a nuvem de palavras.

1. Outros plugins devem ser aplicados de forma global, no site principal que cuida das revistas, como exemplo um plugin que exibe as estatísticas de revistas gerenciadas pelo site.

- Identificando qual o estilo de plugin você deve fazer, fica mais simples a sua criação.

## 2.1 - Arquivos básicos para a criação do plugin

- Devemos estar localizados na pasta blocks, a qual fica dentro da pasta plugins, que por sua vez fica dentro da pasta do OJS.

- Estando nesta pasta, devemos criar uma pasta com o nome de nosso novo plugin. Façamos isso pelo seguinte código:

```bash
mkdir Nome_Plugin
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

## 2.2 - Programando o Plugin

### 2.2.1 - Index.php

- O arquivo index.php é um carregador simples. Nele deve conter o código que instância a classe principal do seu plugin e retorna uma nova instância do mesmo plugin. Podemos ver um exemplo abaixo:

```php
 <?php

require_once('NomePluginBlockPlugin.php');

return new NomePluginBlockPlugin();

?>
```

### 2.2.2 - version.xml

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

### 2.2.3 - NomePluginBlockPlugin.php

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

### 2.2.4 - block.tpl

- Por fim, o block.tpl é responsável pela exibição de nosso plugin. Assim, o que conter nele será exibido ao habilitarmos o plugin em nosso site.

```php
<div class="pkp_block">
    Texto: {$ola} 
</div>
```

## 2.3 - Como instalar o plugin na sua revistas

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