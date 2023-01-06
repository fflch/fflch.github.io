---
layout: default
title: Moodle
parent: Tutoriais
nav_order: 2
---
1. TOC
{:toc}
---


# Tutorial Moodle

## 0.Pré-requisitos para a instalação

Para instalar o moodle é necessário que o seu computador possua a versão 7.4 do PHP:

**Para instalar o PHP e todas as extensões:**

```
sudo apt-get update && sudo apt-get upgrade
sudo apt install php7.4 php-intl php-mysql php-gd pho-xml php-mbstring php-zip php-curl
sudo apt install php-curl
```

**O Moodle utiliza o MariaDB como banco de dados, para o instalar:**

```
sudo apt install mariadb-server
mariadb -uadmin -psenha
```

**Para instalar o composer:**
```
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

## 1.Instalação e Configuração do GitHub

Para fazer download do Moodle é necessario antes possuir o GitHub configurado. Para isto siga os passos a diante:

*Atenção, para seguir os passos você deve possuir uma conta ativa no GitHub*
    
**Para instalar o Git:**

```
sudo apt install git
git config --global user.name "Seu nome de usuário"
git config --global user.email "Seu e-mail do GitHub"
```

**Para fazer a clonagem do projeto:**

Para a criação de um diretório onde o arquivo vai ficar:

```
mkdir caminho\caminho
```

Com o GitHub podemos clonar um projeto da plataforma para o nosso computador, para fazer a clonagem do moodle4:

```
git clone https://github.com/fflch/moodle4_composer
```

## 2.Instalação e Configuração do Moodle 

Após a realização da clonagem acesse a pasta do moodle4:
    
```
cd moodle4
composer install
```
Para subir o moodle em uma porta:

```
php -S 0.0.0.0:9999 -t moodle
```

*Pronto, o Moodle4 foi instalado com sucesso!*

# Criação de um plugin no Moodle 

Neste tutorial vamos aprender como instalar um plugin que apresenta o número de atividades entregues por alunos que estão online na plataforma:

    



    