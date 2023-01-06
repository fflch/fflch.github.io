---
layout: default
title: OJS
parent: Tutoriais
nav_order: 5
---
1. TOC
{:toc}
---



# 0 - Preparação da infraestrutura de desenvolvimento do OJS

Instalação dos componentes basicos para desenvolvermos o OJS usando Debian e derivadios. Verifique o procedimento correspondente para o seu sistema operacional.

## 0.0 - Instalar o Terminator

- Opcionalmente você pode instalar o Terminator, um terminal mais dinamico. 

```
sudo apt install terminator
```

## 0.1 - Instalando o PHP para uso do OJS

- O PHP é essencial para o funcionamento do OJS, sendo ele tambem a linguagem a ser utilizada para a programação dos plugins

```
sudo apt install php php-intl php-mysql php-gd php-xml php-mbstring php-zip php-curl
```

## 0.2 - Instalando e configurando o git

- O git é de extrema necessidade para o meio de trabalho cooperativo, nele você poderá compartilhar o seus projetos.

```
sudo apt install git
git config --global user.name "Seu user cadastrado no GitHub"
git config --global user.email "Seu email cadastrado no GitHub"
```
Criar conta no GitHub e adicionar a chave pública gerada desta forma:

```
ssh-keygen
cat ~/.ssh/id_rsa.pub
```

## 0.3 - Instalar e configurar o banco de dados MariaDB

- O OJS requere do usuario um banco de dados, o MariaDB é um dos melhores do mercado e de facil compreenção e utilização pelo usuario.

```
sudo apt install mariadb-server
sudo mariadb
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%'  IDENTIFIED BY 'admin' WITH GRANT OPTION;
quit
exit
```

## 0.4 - Instalando o Visual Studio Code

- O Visual Studio Code é uma das ferramentas mais utilizadas para se criar e editar códigos. Sua instalação é opcional, mas é de extrema ajuda ao programar.

```
sudo apt install code
```

## 0.5 - Baixando e instalando o Composer

- O Composer é uma ferramenta para gerenciamento de dependências em PHP. 

```
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

## 0.6 - Baixando e instalando o OJS

- O OJS é a ferramenta de gerenciamento de revistas utilizado na USP. A versão que devemos utilizar é a versão 3.3.0-13.

1. Primeiramente devemos baixar o OJS por meio do seguinte código: 

```
wget https://pkp.sfu.ca/ojs/donwload/ojs-3.3.0-13.tar.gz
```

2. Após isso, devemos descompactar o OJS pro meio do código:

```
tar -vzxf ojs-3.3.0-13.tar.gz
```

- Com isso, o OJS estará funcionando perfeitamente em sua maquina.

## 0.7 - Configurando o MariaDB para o OJS

- O MariaDB vem com tabelas definidas, para utilizarmos o OJS devemos criar uma tabela especial para ele.

```
mariadb -uadmin -padmin
Create table ojs3;
quit
exit
```

## 0.8 - Iniciando o OJS

- Para a inicialização do OJS é preciso que estejamos na pasta em que ele esta instalado. Já na pasta, devemos inicializar o OJS pelo seguinte código:

```
php -S 0.0.0.0:8888
```

# 1 - Como configurar o OJS

# 2 - Criar um plugin do tipo Block

- O OJS, assim como outras plataformas, tem varios estilos de plugin. Na presente parte vamos explicar passo a passo a criar um plugin do estilo bloco.

## 2.1 - Arquivos basicos para a criação do plugin

- Devemos estar localizados na pasta blocks, a qual fica dentro da pasta plugins, que por sua vez fica dentro da pagina do OJS.

- Estando nesta pasta, devemos criar uma pasta com o nome de nosso novo plugin. Façamos isso pelo seguinte código:

```
mkdir Nome_Plugin
```

- Com isso, devemos criar uma pasta chamada templates. Façamos isso pelo seguinte código:

```
mkdir templates
```

- Após isso devemos criar os arquivos Index, Nome_PluginBlockPlugin.inc.php, o settings.xml e o version.xml. Façamos isso a partir dos seguintes códigos:

```
touch index.php
touch Nome_PluginBlockPlugin.inc.php
touch settings.xml
touch version.xml
```

- Após a criação dos arquivos, devemos entrar na pagina templates e criar o arquivo block.tpl. Façamos isso atraves do código:

```
touch block.tpl
```

## 2.2 - Criando o Plugin


![Logo do OJS](/assets/images/ojs.png)