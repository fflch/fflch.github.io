---
layout: default
title: Treinamento Laravel
parent: Tutoriais
nav_order: 1
---
1. TOC
{:toc}
---

# Dia 1

## Instalação 

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
## MVC 

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

Criando um arquivo para a view:

```php
mkdir resources/views/exercises
touch resources/views/exercises/index.blade.php
echo "Ola" >  resources/views/exercises/index.blade.php
```

Como retornar uma view no controller:

```php
return view('exercises/index.blade.php');
#ou 
return view('exercises.index');
```

Conteúdo mínimo de index.blade.php:

```html
<!DOCTYPE html>
<html>
    <head>
        <title>treinamento</title>
    </head>
    <body>
        Uma view melhor...
    </body>
</html>
```

Retornando uma view passando variáveis para o template:

```php
return view('exercises.index', [
    'variavel1' => 'qualquer'
]);
```

```bash
php artisan make:model Exercise -m
```
Colocar duas colunas: 

```php
$table->string('diet');
$table->integer('pulse');
```

## Tinker

Criando um registro:

```php
php artisan tinker
$exercise = new App\Models\Exercise;
$exercise->diet = "low fat";
$exercise->pulse = 95;
$exercise->save();
quit
```

Listando registro no index:

```php
public function index(){
    $exercises = App\Models\Exercise:all();
    return view('exercises.index',[
        'exercises' => $exercises
    ]);
}
```

No blade:

```php
{% raw %}
@forelse ($exercises as $exercise)
    <li>{{ $exercise->diet }}</li>
    <li>{{ $exercise->pulse }}</li>
@empty
    Não há livros cadastrados
@endforelse
{% endraw %}
```

## Command 

Criando um comando no laravel:

```php
php artisan make:command ImportaExerciseCsv
```

Que gera o arquivo:  **app/Console/Commands/ImportaExerciseCsv.php**, no qual devemos definir o comando em si:

```php
protected $signature = 'ImportaExerciseCsv';
```
No método *handle()* definimos nossa lógica.

## Exercício 1

1) Criar uma rota e um método novo no controler chamado stats e mostrar a quantidade de linhas do tipo **rest**, **walking** e **running**. Também mostar a média da coluna **pulse** nos três casos **rest**, **walking** e **running**, tudo referente ao arquivo:

[https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv](https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv)

Exemplo de saída:

|  exercise.csv| rest  | walking   | running |
|--------------|-------|-----------|---------|
|  Qtde linhas |  XX   |     XX    |   XXX   | 
|  Média Pulse |  XX   |     XX    |   XXX   |

2) Criar uma rota e um método novo no controler que importa cada linha do csv no banco de dados, assim como fizemos com o tinker.


# Dia 2

## CRUD

Operações básicas sob o Model: Create (Criação), Read (Consulta), Update (Atualização) e Delete (Destruição)

No dia 1 criamos o Model Exercise e dois campos: diet e pulse.
Nesta parte vamos criar um novo model Chamado Livro e correspondente migration, com os campos:

```php
$table->string('titulo');
$table->string('autor')->nullable();
$table->string('isbn');
```

### Create

Rotas para mostrar o formulário de cadastro de Livro:

```php
use App\Http\Controllers\LivroController;
Route::get('/livros/create', [LivroController::class,'create']);
Route::post('/livros', [LivroController::class,'store']);
```

Método *create* para mostrar o formulário html:

```php
public function create()
{
    return view('livros.create');
}
```

Formulário html:
```php
<form method="POST" action="/livros">
    @csrf
    Título: <input type="text" name="titulo">
    Autor: <input type="text" name="autor">
    ISBN: <input type="text" name="isbn">
    <button type="submit">Enviar</button>
</form>
```

### Read

Temos dois acessos aos dados. O acesso a um livro específico e uma listagem.

```php
use App\Http\Controllers\LivroController;
Route::get('/exercises', [LivroController::class,'index']);
Route::get('/exercises/{livro}', [LivroController::class,'show']);
```

Controllers:
```php
public function index()
{
    $livros =  Livro::all();
    return view('livros.index',[
        'livros' => $livros
    ]);
}

public function show(Livro $livro)
{
    return view('livros.show',[
        'livro' => $livro
    ]);
}
```

html para index:
```php
{% raw %}
@forelse ($livros as $livro)
    <ul>
        <li><a href="/livros/{{$livro->id}}">{{ $livro->titulo }}</a></li>
        <li>{{ $livro->autor }}</li>
        <li>{{ $livro->isbn }}</li>
    </ul>
@empty
    Não há livros cadastrados
@endforelse
{% endraw %}
```

### Update

Novamente temos que mostrar o fomulário de edição e um método para salvar:
```php
use App\Http\Controllers\LivroController;
Route::get('/exercises/{livro}', [LivroController::class,'edit']);
Route::post('/exercises/{livro}', [LivroController::class,'update']);
```

Implementação no controller:
```php
public function edit(Livro $livro)
{
    return view('livros.edit',[
        'livro' => $livro
    ]);
}

public function update(Request $request, Livro $livro)
{
    $livro->titulo = $request->titulo;
    $livro->autor = $request->autor;
    $livro->isbn = $request->isbn;
    $livro->save();
    return redirect("/livros/{$livro->id}");
}
```

Html para edição:
```php
{% raw %}
<form method="POST" action="/livros">
    @csrf
    Título: <input type="text" name="titulo" value="{{ $livro->titulo }}">
    Autor: <input type="text" name="autor" value="{{ $livro->autor }}">
    ISBN: <input type="text" name="isbn" value="{{ $livro->isbn }}">
    <button type="submit">Enviar</button>
</form>
{% endraw %}
```

### Delete

Rota para delete:
```php
Route::delete('/exercises/{livro}', [LivroController::class,'update']);
```

Controller para delete:
```php
public function destroy(Livro $livro)
{
    $livro->delete();
    return redirect('/livros');
}
```

Botão html para delete:
```php
{% raw %}
<li>
    <form action="/livros/{{ $livro->id }} " method="post">
    @csrf
    @method('delete')
    <button type="submit" onclick="return confirm('Tem certeza?');">Apagar</button> 
    </form>
</li>
{% endraw %}
```
## Exercício 2

1. Criar um model Book com migration e um controller BookController
2. Na migration criar os campos https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv
3. Criar uma rotina de importação com **php artisan make:command ImportBookCsv** e importa o csv https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv (esse é o completo!)
4. Implementar todos médodos do CRUD, de forma que pela inteface poderemos criar, editar, ver e apagar books
5. Criar rota, controler e view que vai mostrar: 

    - uma tabela com a quantidade de livros por ano
    - uma tabela com a quantidade de livros por autor
    - uma tabela com a quantidade de livros por idioma

# Dia 3

Instalação do template USP conforme:

[https://github.com/uspdev/laravel-usp-theme/blob/master/docs/configuracao.md](https://github.com/uspdev/laravel-usp-theme/blob/master/docs/configuracao.md)

## Validação

### Validação no Controller

Quando estamos dentro de um método do controller, a forma mais rápida de validação é
usando `$request->validate`, que validará os campos com as condições que 
passarmos e caso falhe a validação, automaticamente o usuário é retornado 
para página de origem com todos inputs que foram enviados na requisição, além da
mensagens de erro:

{% highlight php %}
$request->validate([
  'titulo' => 'required',
  'autor' => 'required',
  'isbn' => 'required|integer',
]);
{% endhighlight %}

Podemos usar a função `old('titulo')` nos formulários, que 
verifica se há inputs na sessão e em caso negativo usa o segundo parâmetro:

{% highlight html %}
{% raw %}
Título: <input type="text" name="titulo" value="{{old('titulo')}}">
Autor: <input type="text" name="autor" value="{{old('autor')}}">
ISBN: <input type="text" name="isbn" value="{{old('isbn')}}">
{% endraw %}
{% endhighlight %}

### FormRequest

A validação, que muitas vezes será idêntica no store e no update, pode ser
delegada para um FormRequest. Crie um FormRequest com o artisan:

{% highlight bash %}
php artisan make:request LivroRequest
{% endhighlight %}

Esse comando gerou o arquivo `app/Http/Requests/LivroRequest.php`. Como
ainda não falamos de autenticação e autorização, retorne `true` no método
`authorize()`. As validações podem ser implementada em `rules()`.
Perceba que o isbn pode ser digitado com traços ou ponto, mas eu
só quero validar a parte numérica do campo e ignorar o resto, 
para isso usei o método `prepareForValidation`:

{% highlight php %}
public function rules(){
    $rules = [
        'titulo' => 'required',
        'autor'  => 'required',
        'isbn' => 'required|integer',
    ];
    return $rules;
}
protected function prepareForValidation()
{
    $this->merge([
        'isbn' => preg_replace('/[^0-9]/', '', $this->isbn),
    ]);
}
{% endhighlight %}

Não queremos livros cadastrados com o mesmo isbn. Há uma validação
chamada `unique` que pode ser invocada na criação de um livro como 
`unique:TABELA:CAMPO`, mas na edição, temos que ignorar o próprio livro
assim `unique:TABELA:CAMPO:ID_IGNORADO`. Dependendo do
seu projeto, talvez seja melhor fazer um formRequest para criação e 
outro para edição. Aqui usaremos o mesmo FormRequest para ambos. 
As mensagens de erros podem ser customizadas com o método `messages()`:

{% highlight php %}
public function rules(){
    $rules = [
        'titulo' => 'required',
        'autor'  => 'required',
        'isbn' => ['required','integer'],
    ];
    if ($this->method() == 'PATCH' || $this->method() == 'PUT'){
        array_push($rules['isbn'], 'unique:livros,isbn,' .$this->livro->id);
    }
    else{
        array_push($rules['isbn'], 'unique:livros');
    }
    return $rules;
}
protected function prepareForValidation()
{
    $this->merge([
        'isbn' => str_replace('-','',$this->isbn)
    ]);
}
public function messages()
{
    return [
        'isbn.unique' => 'Este isbn está cadastrado para outro livro',
    ];
}
{% endhighlight %}

## Migration de alteração
Quando o sistema está produção, você nunca deve alterar uma migration que já foi
para o ar, mas sim criar uma migration que altera uma anterior. Por exemplo, 
se quisermos que o campo isbn guarde apenas números, faremos:

{% highlight bash %}
composer require doctrine/dbal
php artisan make:migration change_isbn_column_in_livros  --table=livros
{% endhighlight %}

Para usar migration de alteração devemos incluir o pacote `doctrine/dbal` e
na sequência criar a migration que alterará a tabela existente.

Alterando a coluna `isbn` de string para integer na migration acima:
{% highlight php %}
$table->integer('isbn')->change();
{% endhighlight %}

Aplique a mudança no banco de dados:
{% highlight bash %}
php artisan migrate
{% endhighlight %}

## Campos do tipo select 

Vamos supor que queremos um campo adicional na tabela de livros
chamado `tipo`. Já sabemos como criar uma migration de alteração
para alterar a tabela livros:

{% highlight bash %}
php artisan make:migration add_tipo_column_in_livros --table=livros
{% endhighlight %}

E adicionamos na nova coluna:
{% highlight php %}
$table->string('tipo');
{% endhighlight %}

Vamos trabalhar com apenas dois tipos: nacional e internacional.
A lista de tipos poderia vir de qualquer fonte: outro model, api,
csv etc. No nosso caso vamos fixar esse dois tipos em um array e
usar em todo o sistema. No model do livro vamos adicionar um método
estático que retorna os tipos, pois assim, fica fácil mudar caso 
a fonte seja alterada no futuro:

{% highlight php %}
public static function tipos(){
    return [
        'Nacional',
        'Internacional'
    ];
}
{% endhighlight %}

No `form.blade.php` podemos inserir o tipo com um campo select desta forma:
{% highlight html %}
{% raw %}
<select name="tipo">
    <option value="" selected=""> - Selecione  -</option>
    @foreach ($livro::tipos() as $tipo)
        <option value="{{$tipo}}" {{ ( $livro->tipo == $tipo) ? 'selected' : ''}}>
            {{$tipo}}
        </option>
    @endforeach
</select>
{% endraw %}
{% endhighlight %}

Se quisermos contemplar o `old` para casos de erros de validação:
{% highlight html %}
{% raw %}
<select name="tipo">
    <option value="" selected=""> - Selecione  -</option>
    @foreach ($livro::tipos() as $tipo)
        {{-- 1. Situação em que não houve tentativa de submissão --}}
        @if (old('tipo') == '')
        <option value="{{$tipo}}" {{ ( $livro->tipo == $tipo) ? 'selected' : ''}}>
            {{$tipo}}
        </option>
        {{-- 2. Situação em que houve tentativa de submissão, o valor de old prevalece --}}
        @else
            <option value="{{$tipo}}" {{ ( old('tipo') == $tipo) ? 'selected' : ''}}>
                {{$tipo}}
            </option>
        @endif
    @endforeach
</select>
{% endraw %}
{% endhighlight %}

Por fim, temos que validar o campo tipo para que só entrem os valores do nosso array.
No LivroRequest.php:

{% highlight php %}
use Illuminate\Validation\Rule;
...
'tipo'   => ['required', Rule::in(\App\Models\Livro::tipos())],
{% endhighlight %}

## Mutators

Há situações em que queremos fazer um leve processamento antes de salvar
um valor no banco de dados e logo após recuperarmos um valor. Vamos 
adicionar um campo para preço. Já sabemos como criar uma migration 
de alteração para alterar a tabela livros:

{% highlight bash %}
php artisan make:migration add_preco_column_in_livros --table=livros
{% endhighlight %}

E adicionamos na nova coluna:
{% highlight php %}
$table->float('preco')->nullable();
{% endhighlight %}

No LivroRequest também deixaremos esse campo como 
opcional: `'preco'  => 'nullable'`. 

Queremos que o usuário digite, por exemplo, `12,50`, mas guardaremos
`12.5`. Quando quisermos mostrar o valor, vamos fazer a operação
inversa. Poderíamos fazer esse tratamento diretamente no controller,
mas também podemos usar `mutators` diretamente no model do livro:

{% highlight php %}
public function setPrecoAttribute($value){
    $this->attributes['preco'] = str_replace(',','.',$value);
}

public function getPrecoAttribute($value){
    return number_format($value, 2, ',', '');
}
{% endhighlight %}

## Exercício 3

Esse exercíco é referente ao arquivo: https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/country_data/Brazil.csv

1. Criar model, migration, CRUD, command de importação do csv. Na migration defina os campos total_vaccinations e	people_vaccinated como string. Importe o csv.
2. Faça uma migration de alteração para alterar total_vaccinations e people_vaccinated para inteiro
3. Faça um mutator para mostrar o campo date com o formato brasileiro dd/mm/yyyy e outro mutator para salvá-lo commo yyyy-mm-dd (lembre-se que o formulário deve receber dd/mm/yyyy)
4. Implemente o FormRequest garantindo que seja digitado dd/mm/yyyy, além implementar as outras validações
5. Corriga seus formulários para sempre conterem a função old()

# Dia 4 (Em construção)

## Relações

One (User) To Many (Livros)

Primeiramente vamos implementar esse relação no nível do banco de dados.
Na migration dos livros insira:

{% highlight php %}
$table->unsignedBigInteger('user_id')->nullable();
$table->foreign('user_id')->references('id')->on('users')->onDelete('set null');;
{% endhighlight %}

No model Livro podemos criar um método que carregará o objeto
`user` automaticamente ou no model `User` podemos carregar todos
livros do usuário:

{% highlight php %}
class Livro extends Model
{
    public function user(){
        return $this->belongsTo(\App\Models\User::class);
    }
}

class User extends Model
{
    public function livros()
    {
        return $this->hasMany(App\Models\Livro::class);
    }
}
{% endhighlight %}

Assim no `fields.blade.php` faremos referência direta  a esse usuário:

{% highlight html %}
{% raw %}
<li>Cadastrado por {{ $livro->user->name ?? '' }}</li>
{% endraw %}
{% endhighlight %}


# Extra

Configuração do .env para conexão com banco de dados:

```bash
DB_DATABASE=treinamento                                                                                                           
DB_USERNAME=admin                                                                                                                 
DB_PASSWORD=admin
```


Criando model e tabela no banco de dados:

## biblioteca Audit

O módulo Audit é uma forma de verificar e manter registros das modificações feitas por usuários no sistema.

1. Instalação
- O pacote é instalado via Composer. Para o obter é necessário executar este comando dentro da pasta do seu projeto:

```bash
composer require owen-it/laravel-auditing
```

 2. Configuração 
- Após isso, use o comando a seguir para publicar as configurações feitas e criar o arquivo **config/audit.php**:

```bash
php artisan vendor:publish --provider "OwenIt\Auditing\AuditingServiceProvider" --tag="config"
```
3. Migration
- A seguir, crie a tabela audits com o seguinte comando: 

```bash
php artisan vendor:publish --provider "OwenIt\Auditing\AuditingServiceProvider" --tag="migrations"
```
```bash
php artisan migrate
```

 4. Model
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

 5. Implementação

 Agora vamos implementar o módulo para ser exibido nas views. 

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
{% raw %}
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
{% endraw %}
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
 Para mais informações visite: <a href="https://laravel-auditing.com/">Laravel Auditing</a>
---
Escrito por Isabela
![Logo do Laravel](/assets/images/laravel.png)
