---
layout: default
title: Drupal
parent: Tutoriais
nav_order: 4
---
1. TOC
{:toc}
---

# **Importação de Arquivos CSV para Drupal**

## **1. Configuração do Ambiente Drupal**

Antes de realizar a importação de arquivos CSV, é necessário instalar e configurar o ambiente Drupal em sua máquina, seguindo os seguintes procedimentos em seu terminal;

- **Instalação do Composer:**

```bash
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```
- **Download e Instalação das Dependências:**

Em seu navegador, acesse https://github.com/fflch/drupal e crie um fork do repóstório no botão presente no canto superior direito *Fork*. Em seguida, execute o comando abaixo no terminal:

```bash
git clone git@github.com:SEU-USERNAME/drupal.git
cd drupal
composer install
```
<span style="font-family:Arial; font-size:1em;"> ***Observação:** Ao final dessa operação o repositório **drupal** será adicionado a sua máquina.* </span>

- **Servidor HTTP Básico:**

Para habilitar o servidor HTTP, execute o comando abaixo dentro do repositório _**drupal**_ criado acima.
```bash
./vendor/bin/drupal serve 
```

## **2. Acesso ao Modo Administrador na Página Drupal**

- Ao acessar o link presente ao se subir o Servidor HTTP Básico, basta adicionar a barra de endereço web o complemento */user*. Ficando então com o seguinte endereço:

![Barra Web](/assets/images/Drupal/Barra%20Web.png)

<span style="font-family:Arial; font-size:1em;"> ***Observação:** O complemento **/login** é inserido automaticamente na barra de pesquisa.*

- Ao se encontrar na página de login, realize o login utilizando o ***user*** e ***senha*** fornecidos por seu supervisor, além de responder coretamente o desafio.

![Tela Login](/assets/images/Drupal/Tela%20Login.png)

- Na tela seguinte, clique em *Gerenciar* para acessar demais passos do tutorial.

![Tela Inicial](/assets/images/Drupal/Tela%20Inicial.png)

## **3. Preparação para Importação do Arquivo CSV**

### **3.1 Criação do Tipo de Conteúdo**

- Antes de realizar a importação de dados do arquivo CSV para o sistema Drupal, é necessário realizar através da interface gráfica do Drupal a criação do tipo de contéudo. E para isso, após entrar na tela inicial e realizar o passo acima, é preciso ir em ***Estrutura***, ***Tipos de Conteúdo***.

![Passo 1](/assets/images/Drupal/Passo%201.png)

![Passo 2](/assets/images/Drupal/Passo%202.png)

- Em *Tipos de Conteúdo*, clique em ***Adicionar tipo de conteúdo***.

![Passo 3](/assets/images/Drupal/Passo%203.png)

- Na interface de *Adicionar tipo de conteúdo*, insira o nome do conteúdo e salve.

![Passo 4](/assets/images/Drupal/Passo%204.png)
![Passo 5](/assets/images/Drupal/Passo%205.png)

- Após o tipo de conteúdo ser salvo, a seguinte tela com o campo *body* será criado. Realize a exclusão desse campo, pois este não será necessário.

![Passo 6](/assets/images/Drupal/Passo%206.png)
![Passo 7](/assets/images/Drupal/Passo%207.png)

### **3.2 Criação dos Campos do Conteúdo**
![Print](/assets/images/Drupal/Print.png)

Além da criação do conteúdo referente a planilha que será importada, é também necessária a criação manual dos campos presentes no documento. 

- Para isso é necessário ir em ***Adicionar campo***.

![Passo 8](/assets/images/Drupal/Passo%208.png)

- ***Selecionar um tipo de campo*** referente as informações presentes na tabela a ser importada, e clicar em ***Save and continue***.
![Passo 9](/assets/images/Drupal/Passo%209.png)

- Nas páginas seguintes mantenha as configurações básicas e salve.
![Passo 10](/assets/images/Drupal/Passo%2010.png)

<span style="font-family:Arial; font-size:1em;"> ***Observação:** Em exportação de arquivos que possuam mais de informação relacionada a ele, é necessário alterar o Números de valores permitidos de Limitado para Ilimitado.* </span>

- Ao fim desses passos, a página *Gerenciar campos* estará similiar ao exemplo. Nesse passo, fique atento ao ***Nome de Máquina*** referente aos campos criados.

![Passo 11](/assets/images/Drupal/Passo%2011.png)

## **4. Importando um Arquivo CSV**

A importação dos dados presentes em um Arquivo CSV para o sistema Drupal é realizada através de um script. Que lê as linhas de informações e as armazena no sistema de banco de dados do Drupal, possibilitando assim a optimização de tempo do usuário, que realiza a ação de maneira mais prática e automatizada. 

### **4.1. Importação de Arquivo CSV**

- Para criar e rodar o script necessário para importação, escolha um editor de texto de sua preferência. Insira o código abaixo, realizando as alterações necessárias que se encaixem no arquivo o qual esteja trabalhando.

```php 
<?php

use \Drupal\node\Entity\Node; // Declara que a entidade Node será utilizada.
use \Drupal\file\Entity\File; // Declara que a entidade File será utilizada.

//Declara que a variável trará o conteúdo presente no caminho.
$livrocsv = file_get_contents('/home/aline/Biblioteca/livros.csv');
$livros = explode(PHP_EOL, $livrocsv);      //Linha de código que realiza a leitura do arquivo.
$livros_array = array();                    //Cria uma lista, ou Array.

//Declara e define que o array realiza a coleta de dados através das linhas presentes na planilha.
foreach ($livros as $livro) {                   
    $livros_array[] = str_getcsv($livro);
    }

array_pop($livros_array);   //Extrai as informações finais do array criado acima.

//Define e atribui as informações presentes no array que devem ser importadas ao Drupal.
foreach($livros_array as $campo) {
    
    $node = Node::create([
        'type'                             => 'livros',
        'uid'                              => 1,
        'title'                            => $campo[0],
        'field_titulo'                     => $campo[0],
        'field_ano'                        => $campo[1],
        'field_autor'                      => $campo[2],
    ]);

echo $node->save();         //Salva toda a operação feita acima.

}
```
<span style="font-family:Arial; font-size:1em;"> ***Observação:** Se na planilha houver a linha contendo o título das colunas, será necessário deletá-la. Pois, o script realiza a leitura de todas as linhas da planilha, incluindo as de título.*

- Em seguida, execute o comando _./vendor/bin/drush php-script_ + o caminho contendo o script salvo, **dentro do repositório drupal**.

```bash
./vendor/bin/drush php-script /home/aline/Biblioteca/Script_Biblio.php 
```
Após a conclusão dos passos acima, a área **Conteúdo** não estará mais vazia e os arquivos do tipo de conteúdo criados serão listados conforme o exemplo abaixo.
![Print 2](/assets/images/Drupal/Print%202.png)

E dentro de cada um dos conteúdos, a informação será apresentada conforme preenchida na planilha e na ordem citada no script.

![Print 3](/assets/images/Drupal/Print%203.png)

### **4.1. Importação de Arquivo CSV com PDF**

Para inserir arquivos de imagem, pdf e outros, referentes ao Arquivo CSV a ser importado, é necessário que os documentos complementares sejam nomeados com trechos, ou nomes de informações presentes no CSV. Em nosso exemplo, criamos um repositório chamado "Capas", que contém as capas dos títulos refereciando os nomes dos livros.

![Pasta](/assets/images/Drupal/Pasta.png)

- Além da necessidade da nomeação ser referente as informações presentes na planilha, também a necessária a criação de um novo campo do tipo _**Arquivo**_ no qual deverá ser especificado o formato no qual o arquivo está salvo. No caso do nosso exemplo, os arquivos estão salvos no formato **PNG**.

![Campo Arquivo 1](/assets/images/Drupal/Campo%20Arquivo%201.png)
![Campo Arquivo 2](/assets/images/Drupal/Campo%20Arquivo%202.png)

- Para está ação, o script também sofre algumas mudanças, ficando da seguinte maneira.

```php 
<?php


use \Drupal\node\Entity\Node;
use \Drupal\file\Entity\File;

$livrocsv = file_get_contents('/home/aline/Biblioteca/livros.csv');
$livros = explode(PHP_EOL, $livrocsv);
$livros_array = array();

foreach ($livros as $livro) {
    $livros_array[] = str_getcsv($livro);
    }

array_pop($livros_array);

//Define o caminho onde a pasta contendo os arquivos se encontra.
$full_path= '/home/aline/Biblioteca/Capas/';
//Retorna um array de arquivos e diretórios dentro de um directory.
$capaspdf= scandir($full_path);

foreach($livros_array as $campo) {
    $titulo = $campo[0];
    $capas_relacionadas = [];
   
    foreach($capaspdf as $capapdf){
        if(str_contains($capapdf, $titulo)){
            $capas_relacionadas[] = $capapdf;
        }
    }
    
    $node = Node::create([
        'type'                             => 'livros',
        'uid'                              => 1,
        'title'                            => $campo[0],
        'field_titulo'                     => $campo[0],
        'field_ano'                        => $campo[1],
        'field_autor'                      => $campo[2],
    ]);
    
    $Capas_PDF = [];
    foreach($capas_relacionadas as $capa_relacionada){
        $capa_conteudo = file_get_contents($full_path.$capa_relacionada);
        $file = file_save_data($capa_conteudo, 'public://'.$capa_relacionada, FILE_EXISTS_REPLACE);
        $Capas_PDF[] = [
            'target_id' => $file->id(),
            'alt'       => 'Arquivo' . $file->id(),
            'title'     => 'Capa PDF',
        ];
    }

    $node->set('field_capa', $Capas_PDF);

echo $node->save();

}
```
Ao fim da operação as informações presentes na planilha + os arquivos externos linkados a ela serão importados ao drupal. Ficando algo similar ao exemplo.

![Print 4](/assets/images/Drupal/Print%204.png)

Escrito por Aline Maire 