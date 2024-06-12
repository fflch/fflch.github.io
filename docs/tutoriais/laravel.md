---
layout: default
title: Laravel
parent: Tutoriais
nav_order: 1
---
1. TOC
{:toc}
---

# Treinamento Laravel

## Dia 1

### Instalação 

Biblioteca mínimas para instalação no debian 12:

```bash
sudo apt-get install php php-common php-cli php-gd php-curl php-xml php-mbstring php-zip php-sybase php-mysql php-sqlite3
sudo apt-get install mariadb-server sqlite3 git
```

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

Instalação do composer:

```bash
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

Criação de usuário admin com senha admin e criação de uma banco chamado drupal:
```bash
sudo mariadb
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%'  IDENTIFIED BY 'admin' WITH GRANT OPTION;
create database treinamento;
quit
```

Criando um projeto laravel:

```bash
composer create-project laravel/laravel treinamento
cd treinamento
php artisan serve
```

Criando a primeira rota:

```php
Route::get('/exercises', function () {
    echo "Uma rota sem controller, not good!";
});
```

Criando o controller ExerciseController:
```php
php artisan make:controller ExerciseController
```

Agora sim uma rota com controller:

```php
use App\Http\Controllers\ExerciseController;
Route::get('/exercises', [ExerciseController::class,'index']);
```



### Exercício 1

Mostrar no seu controller quantidade de linhas do seguinte arquivo csv do tipo **rest**, **walking** e **running**. Também mostar a média da coluna **pulse** nos três casos **rest**, **walking** e **running**:

[https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv](https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv)

Exemplo de saída:

|  exercise.csv| rest  | walking   | running |
|--------------|-------|-----------|---------|
|  Qtde linhas |  XX   |     XX    |   XXX   | 
|  Média Pulse |  XX   |     XX    |   XXX   |

rest


# Dia 2
# Dia 3
# Dia 4
# Dia 5

### O módulo Audit é uma forma de verificar e manter registros das modificações feitas por usuários no sistema.

## 1. Instalação
- O pacote é instalado via Composer. Para o obter é necessário executar este comando dentro da pasta do seu projeto:

```bash
composer require owen-it/laravel-auditing
```

## 2. Configuração 
- Após isso, use o comando a seguir para publicar as configurações feitas e criar o arquivo **config/audit.php**:

```bash
php artisan vendor:publish --provider "OwenIt\Auditing\AuditingServiceProvider" --tag="config"
```

## 3. Migration
- A seguir, crie a tabela audits com o seguinte comando: 

```bash
php artisan vendor:publish --provider "OwenIt\Auditing\AuditingServiceProvider" --tag="migrations"
```
```bash
php artisan migrate
```

## 4. Model
- Para implementar o audit no model desejado, é necessário adicionar as linhas:

```php
use OwenIt\Auditing\Contracts\Auditable;

class Instance extends Model implements Auditable
{
    use HasFactory;
    use \OwenIt\Auditing\Auditable;

    / ...
}    
```

## 5. Implementação

### Agora vamos implementar o módulo para ser exibido nas views. 

- Primeiro, para facilitar a leitura dos usuários, é necessário mapear os campos da migration do Model em que o audit será utilizado. Então, em **app/Utils** vamos criar **Mapeamento.php** para o Model Livro, como no exemplo abaixo:

```php
<?php

namespace App\Utils;

use App\Models\Livro;

class Mapeamento
{
    public static function map($chave){
        $mapeamento = [
            'id' => 'ID',
            'autores' => 'Autores',
            'titulo' => 'Título',
            'editora' => 'Editora',
            'ano' => 'Ano',
            'isbn' => 'ISBN',
        ];

        return $mapeamento[$chave];
    }
}
```

- Agora vamos chamar este mapeamento dentro do Model correspondente:

**app/Models/Livro.php**
```php
use App\Utils\Mapeamento;

class Livro extends Model implements Auditable
{
    / ...

    public function mapeamento($chave) {
        return MapRecords::map($chave);
    }
}
```
- Após isso, é preciso adicionar a exibição do módulo audit nas views, criando uma tabela com as alterações que foram feitas, a data da alteração e o usuário que a realizou. Dentro da pasta **resources/views/livros/partials** vamos criar **audit.blade.php**, já adicionando o mapeamento feito anteriormente na tabela:
**partials/audit.blade.php**

```php
<table class="table table-striped">
  <thead>
    <tr>
      <th scope="col">Data</th>
      <th scope="col">Usuário(a)</th>
      <th scope="col">Campos alterados</th>
      <th scope="col">Alterações</th>
    </tr>
  </thead>
  <tbody>
    @foreach($model->audits as $field => $audit)
        <tr>
        <td> {{ \Carbon\Carbon::parse($audit->getMetadata()['audit_created_at'])->setTimezone('America/Sao_Paulo')->format('d/m/Y H:i') }} </td>
        <td> {{ $audit->getMetadata()['user_name'] }}</td>
        <td> 
            @foreach($audit->getModified() as $field=>$modified)
            @if($field)
                <b>{{ $livro->mapeamento($field) }}: {{ $modified['old'] }}<br>
            @endif
            @endforeach
        </td>
        <td> 
            @foreach($audit->getModified() as $field2=>$modified)
            @if($field)
                <b>{{ $record->mapeamento($field2) }}: {{ $modified['new'] }}<br>
            @endif
            @endforeach
        </td>
        </tr>
    @endforeach
  </tbody>
</table>

```

- Agora vamos incluir a tabela na view **show.blade.php** de livros:

```php
@include('livros.partials.audit', ['model'=>$livro])
```

- Para que a página não fique muito poluída, optamos por inserir a tabela dentro de uma tag details usando um alerta bootstrap, desta forma:

```php
<div class="alert alert-info" role="alert">
    <details>
        <summary>Visualizar histórico de alterações</summary>
        <br>
        @include('livros.partials.audit', ['model'=>$livro])
    </details>
</div>
```
### Para mais informações visite: <a href="https://laravel-auditing.com/">Laravel Auditing</a>
---
Escrito por Isabela
![Logo do Laravel](/assets/images/laravel.png)