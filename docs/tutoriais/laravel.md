---
layout: default
title: Laravel
parent: Tutoriais
nav_order: 1
---
1. TOC
{:toc}
---



# LARAVEL AUDITING

### O módulo Audit é uma forma de verificar e manter registros das modificações feitas por usuários no sistema.

## 1. Instalação
- O pacote é instalado via Composer. Para o obter é necessário executar este comando dentro da pasta do seu projeto:

```
composer require owen-it/laravel-auditing
```

## 2. Configuração 
- Edite o arquivo **config/app.php**, acrescentando a seguinte linha:

```
'providers' => [
    // ...

    OwenIt\Auditing\AuditingServiceProvider::class,

    // ...
],
```
- Após isso, use o comando a seguir para publicar as configurações feitas e criar o arquivo **config/audit.php**:

```
php artisan vendor:publish --provider "OwenIt\Auditing\AuditingServiceProvider" --tag="config"
```

## 3. Migration
- A seguir, crie a tabela audits com o seguinte comando: 

```
php artisan vendor:publish --provider "OwenIt\Auditing\AuditingServiceProvider" --tag="migrations"
```
```
php artisan migrate
```

## 4. Model
- Para implementar o audit no model desejado, é necessário adicionar as linhas:

```
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

```
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
            'desc_fisica' => 'Descrição física',
            'editora' => 'Editora',
            'local_publicacao' => 'Local de publicação',
            'edicao' => 'Edição',
            'ano' => 'Ano',
            'isbn' => 'ISBN',
        ];

        return $mapeamento[$chave];
    }
}
```

- Agora vamos chamar este mapeamento dentro do Model correspondente:

**app/Models/Livro.php**
```
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

```
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

```
@include('livros.partials.audit', ['model'=>$livro])
```

- Para que a página não fique muito poluída, optamos por inserir a tabela dentro de uma tag details usando um alerta bootstrap, desta forma:

```
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

![Logo do Laravel](/assets/images/laravel.png)