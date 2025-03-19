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
O Composer é um gerenciador de dependências para PHP. Ele permite instalar, atualizar e gerenciar bibliotecas e pacotes de forma simples, garantindo que um projeto tenha todas as dependências necessárias. Usaremos o Composer para instalar o Moodle e seus plugins:

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

Vamos criar um plugin básico do tipo bloco no Moodle chamado `estagiarios`. Esse bloco vai simplesmente listar os nomes dos estagiários em forma de texto.  No Moodle, os plugins do tipo bloco seguem uma estrutura de pastas e arquivos específica. Vamos criar a estrutura inicial para o nosso bloco.

```bash
cd blocks
mkdir estagiarios
cd estagiarios
```

Criar o Arquivo `version.php`, que define a versão do plugin e suas dependências:

```php
<?php
defined('MOODLE_INTERNAL') || die(

$plugin->component = 'block_estagiarios';
$plugin->requires  = 2020061500; // Versão mínima do Moodle necessária.
$plugin->version = 2025011401;
```

O arquivo `block_estagiarios.php` contém a lógica principal do bloco:

```php
<?php
defined('MOODLE_INTERNAL') || die();

class block_estagiarios extends block_base {
    public function init() {
        $this->title = get_string('estagiarios', 'block_estagiarios'); 
    }
	
    public function get_content()) {        
        $estagiarios = [
            'João Silva',
            'Maria Souza',
            'Carlos',
            'Ana Costa',
        ];	
        $this->content = new stdClass;
        $this->content->text = '<ul>';
        foreach ($estagiarios as $nome) {
            $this->content->text .= '<li>' . $nome . '</li>';
        }
        $this->content->text .= '</ul>'
        return $this->content;
    }
}
```

Texto mínimos para internacionalização:

```bash
mkdir -p lang/en
mkdir -p lang/pt_br
```

Versão em português em `lang/pt_br/block_estagiarios.php`:

```php
<?php
defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'Estagiários'; // Nome do bloco.
$string['estagiarios'] = 'Lista de Estagiários'; // Título do bloco.
```

Versão em inglês em `lang/en/block_estagiarios.php`:

```php
<?php
defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'Interns'; // Nome do bloco.
$string['estagiarios'] = 'List of Interns';
```

Por fim, podemos podemos ativar nosso plugin pela interface ou com o comando:

```bash
php admin/cli/upgrade.php
```
 
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

<!--
# Tutorial Moodle
 
## 0.Pré-requisitos para a instalação
 
Para instalar o moodle é necessário que o seu computador possua a versão 7.4 do PHP:
 
**Para instalar o PHP e todas as extensões:**
 
```
sudo apt-get update && sudo apt-get upgrade
sudo apt install php7.4 php-intl php-mysql php-gd php-xml php-mbstring php-zip php-curl
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
 
Para fazer download do Moodle é necessário antes possuir o GitHub configurado. Para isto siga os passos a diante:
 
*Atenção, para seguir os passos você deve possuir uma conta ativa no GitHub.*
  
**Para instalar o Git:**
 
```
sudo apt install git
git config --global user.name "Seu nome de usuário"
git config --global user.email "Seu e-mail do GitHub"
ssh-keygen
```
**Na configuração do GitHub é necessário adicionar uma chave pública para validar o acesso**
 
**Para fazer a clonagem do projeto:**
 
Para a criação de um diretório onde o arquivo vai ficar, você deve informar o caminho da pasta:
 
```
mkdir caminho\caminho
```
 
Com o GitHub podemos clonar um projeto da plataforma para o nosso computador, para fazer a clonagem do moodle 4, entre em: <a href="https://github.com/fflch/moodle4_composer">https://github.com/fflch/moodle4_composer</a> e faça o fork do repositório, localizado no lado superior direito da página.

Após isso, clone o repositório, informando o código SSH do seu fork no terminal:
 
```
git clone https://github.com/seu_user/moodle4_composer
```

Também é importante conectar o repositório original com o projeto local:

```
git remote add upstream https://github.com/fflch/moodle4_composer
```
 
## 2.Instalação e Configuração do Moodle
 
Após a realização da clonagem acesse a pasta do moodle4 para realizar a sua instalação:
  
```
caminho moodle4
composer install
```
Para subir o moodle em uma porta e assim poder acessá-lo no computador:
 
```
php -S 0.0.0.0:9999 -t moodle
```
 
*Pronto, o Moodle4 foi instalado com sucesso!*
 
# Criação de um plugin no Moodle
 
Neste tutorial vamos aprender como instalar um plug-in.
 
Plug-ins são ferramentas que podem ser criadas pelo desenvolvedor para adicionar uma função ao programa, você pode utilizá-lo como forma de personalizar o moodle, para que ele melhor atenda às suas necessidades.
 
O plug-in deste tutorial tem como objetivo criar um bloco que apresenta o número de atividades entregues por alunos que estão online na plataforma:
 
## 0. Introdução aos plug-in
 
No tutorial anterior clonamos a pasta do GitHub do moodle para fazermos a sua instalação. Nesta pasta, estão presentes os códigos fontes dos plug-ins que já vem instalados no programa, é importante ter cuidado para não altera-los, tendo em vista que isto pode causar a desconfiguração do moodle.
 
Na imagem abaixo é possível verificar o terminal no caminho: 
 
```
moodle4_composer/moodle/
```
 
![Captura de tela do terminal](/assets/images/f1.png)
  
## 1. Para criar o plug-in
 
Acesse a pasta blocks, que será o local onde o novo plug-in será criado. Para isso acesse a pasta *blocks*  e digite o comando abaixo para criar uma nova pasta.
 
*Aqui chamamos a pasta atv_on como referências aos alunos online, mas você pode escolher outro nome, o comando mkdir serve para indicar a criação de uma nova pasta*
 
```
mkdir atv_on
```
Para criar um arquivo onde serão dados os comandos para a  do nosso programa, digite:
 
```
cd blocks
cat > block_atv.php
```
*Pronto! Agora podemos digitar o código que será a base do nosso plug-in.*
 
Digite o código abaixo, na estrutura exata:
 
```
<?php
 
class block_atv extends block_base {
 
   public function init(){
       $this->title = 'bloco que apresenta as atividades entregues';
   }
 
   public function get_content() {
       global $DB;
 
       $atividades = 'select count(submission) AS total from from mdl_assignsubmission_file';
       $alunos = 'select firstname from mdl_user';
 
       $resultados = $DB->get_record_sql($atividades);
       $estudantes = $DB->get_record_sql($alunos);
 
       $this->content =  new stdClass;
       $this->content->text = 'Este tarefa possui '. $resultados->total .  ' entregues pelos alunos ' . $estudantes;
       return $this->content;
   }
}
```
 
## 2. Para Compreender a estrutura do código
 
A primeira parte do código é padrão para a criação de plug-ins:
 
```
<?php       a linguagem de programação utilizada.
 
class block_atv extends block_base {         Atribuição do nome e tipo de classe.
 
   public function init(){          Estrutura para iniciar a função.
       $this->title = 'bloco que apresenta as atividades entregues';            Título do plug-in.  
   }
```
 
A estrutura abaixo corresponde a da criação de uma função, que é a base do nosso programa:
 
*Posteriormente será descrito no tutorial os passos para obter informações do banco de dados MariaDB.*
 
```   
   public function get_content() {       Estrutura para iniciar a função.
       global $DB;       Discrição do banco de dados utilizado.
 
       $atividades = 'select count(submission) AS total from from mdl_assignsubmission_file';       Seleção das informações da base de dados
       $alunos = 'select firstname from mdl_user';
 
       $resultados = $DB->get_record_sql($atividades);         função para obter os dados do banco de dados.
       $estudantes = $DB->get_record_sql($alunos);        função para obter os dados do banco de dados.
 
       $this->content =  new stdClass;
       $this->content->text = 'Este tarefa possui '. $resultados->total .  ' entregues pelos alunos ' . $estudantes;         Texto que será exibido no código.
       return $this->content;        Para retornar as informações e imprimir o resultado.
   }
}
```
Este é um código simples em linguagem php, você pode mudar a estrutura para que ele apresente outras informações e realize cálculos.
 
## 3. Código para informar a versão atualizada com o plug-in
 
Conforme o código já está pronto, é necessário que seja criado o arquivo que apresenta a informação da versão atualizada do moodle, para isto crie um novo arquivo de texto conforme descrito abaixo:
 
```
cat > version.php
```
*Atenção, neste arquivo o nome deve ser "version.php", não há opção para escolher outro nome.*
 
O código padrão para informar a versão atualizada com o novo plug-in. Atenção, tenha cuidado para sempre informar o nome do componente de forma correta, caso contrário o plug-in não vai funcionar!
 
```
<?php
 
defined('MOODLE_INTERNAL') || die();
 
$plugin->component = 'block_atv';         Atribuição do nome do plug-in, deve ser idêntico ao arquivo com o código.
$plugin->version = 2022198999999;         A versão da atualização, é necessário alterar o número a cada mudança.
```
## 4. Versões em português e inglês para a exibição do plug-in
 
No moodle é necessária a criação de 2 versões de apresentação do código, uma para português e outra para o inglês. Para isso criaremos uma pasta onde serão inseridas as informações.
 
```
mkdir lang
lang
```
 
*É necessário que a pasta esteja com este nome exato, caso contrário o programa não irá funcionar.*
 
Agora que você está dentro da pasta escreva o comando para criar mais 2 pastas, que armazenam as versões em português e inglês.
 
```
mkdir en
mkdir pt_br
```
## 4.1 Versão em inglês do plug-in
 
Acesse a pasta "en" e crie um arquivo com o mesmo nome do primeiro código - block_atv:
 
```
en
cat > block_atv.php
```
Dentro do arquivo é necessário escrever o código de forma igual a descrita abaixo, deve se alterar apenas o texto atribuído à  string pluginname, conforme abaixo:
 
```
<?php
 
defined('MOODLE_INTERNAL') || die();
 
$string['pluginname'] = 'Nome do plug-in em inglês';         Você pode alterar a descrição apenas desta linha após o sinal de igual.   
$string['block_title'] = 'Mineração dados Itarefas';
$string['blockname'] = 'Mineração dados Itarefas';
```
Pronto! A descrição em inglês do plug-in está finalizada.
 
Para sair da pasta:
 
```
...
```
 
## 4.2 Versão em português do plug-in
 
Agora vamos criar uma versão em português do plug-in.
 
Acesse a pasta e crie um arquivo de texto com nome igual ao anterior e do código do programa:
 
```
pt_br
cat > block_atv.php
```
 
Dentro da pasta digite o código abaixo:
 
```
<?php
 
defined('MOODLE_INTERNAL') || die();
 
$string['pluginname'] = 'Nome do plug-in em português';         Você pode alterar a descrição apenas desta linha após o sinal de igual.
```
*Você pode alterar a descrição do pluginname, as demais informações devem ficar de modo exatamente igual.*
 
Pronto! Você terminou de descrever as informações em potuguês e inglês do seu plug-in.
 
# Consulta de dados no MariaDB

Conforme informado anteriormente o MariaDB é o banco de dados utilizado pelo Moodle 4, neste tutorial aprenderemos caminhos básicos para acessar as estruturas.

## 0. Para acessar o MariaDB
 
Conforme mencionado anteriormente, o MariaDB é o banco de dados utilizado pelo moodle, para acessá-lo digite o comando abaixo:
 
```
sudo mariadb -u root -p -h localhost  
```
O console irá pedir as senhas do usuário e do banco de dados, digite-as e aperte *Enter* para entrar.
 
## 1. Para consultar o MariaDB
 
Utilize o comando abaixo para selecionar o banco de dados do Moodle4:
 
```
use moodle4;
```
 
O Moodle4 foi selecionado, para visualizar as bases de dados digite o comando abaixo:
 
```
show tables;
```
Você deve estar vendo uma tela semelhante a esta:
 
![Tabelas do Moodle4 no MariaDB](/assets/images/ft2.png)
 
Como é possível ver, a base de dados do MariaDB é bastante grande, neste tutorial utilizaremos a mdl_user para ter acesso a informação dos usuários. Para acessá-la digite o código abaixo:
 
```
select * from mdl_user;
```
Você deve estar vendo uma tela semelhante a está abaixo:
 
![Tabela de dados dos usuários do Moodle 4 no MariaDB](/assets/images/ft3.png)
 
Como é possível ver, os dados estão organizados em um formato de tabela, quando desejar selecioná-los você deve substituir o asterisco pelo nome da coluna em questão. No código do plug-in o código ficou desta forma:
 
```
select firstname from mdl_user
```
*Dentro do terminal todos os comandos devem terminar com ponto e vírgula, desta forma ( ; ).*
 
Para mudar o dado que deseja consultar basta apenas digitar o comando alterando a o nome da tabela.
 
```
select * from nome da tabela;
```
Pronto! Conseguimos realizar a consulta de dados no MariaDB, além do plug-in você pode criar códigos com diversas outras finalidades e assim melhorar o funcionamento do Moodle4 para o seu uso.
 
Por fim, para sair do MariaDB:
 
```
Exit;
```

# Pronto! Você chegou ao final do tutorial. 

-->
