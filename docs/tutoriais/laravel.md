---
layout: default
title: Laravel
parent: Tutoriais
nav_order: 1
---
1. TOC
{:toc}
---

# Dia 1

## Instalação 

Antes de instalar o Laravel no Debian, é necessário garantir que todas as dependências estejam instaladas. O Laravel depende do PHP e de algumas extensões, além de um banco de dados como MariaDB ou Sqlite. Aqui estão os principais pacotes que devem ser instalados no Debian:

```bash
sudo apt-get install php php-common php-cli php-gd php-curl php-xml php-mbstring php-zip php-sybase php-mysql php-sqlite3
sudo apt-get install mariadb-server sqlite3 git
```

O Composer é um gerenciador de dependências para PHP. Ele permite instalar, atualizar e gerenciar bibliotecas e pacotes de forma simples, garantindo que um projeto tenha todas as dependências necessárias. No Laravel, o Composer é usado para instalar o framework e suas bibliotecas.

```bash
curl -s https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer
```

Além disso, é importante configurar o banco de dados, pois ele será usado para instalar o Laravel. Vamos inicialmente criar um usuário admin com senha admin e criar um banco de dados chamado *treinamento*:

```bash
sudo mariadb
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%'  IDENTIFIED BY 'admin' WITH GRANT OPTION;
create database treinamento;
quit
```

O comando a seguir cria um novo projeto Laravel na pasta treinamento, baixando a estrutura básica do framework e instalando todas as dependências necessárias via Composer, garantindo que o ambiente esteja pronto para o desenvolvimento:

```bash
composer create-project laravel/laravel treinamento
cd treinamento
php artisan serve
```
## MVC 

Uma rota é a forma como o framework define e gerencia URLs para acessar diferentes partes da aplicação. As rotas são configuradas no arquivo routes/web.php (para páginas web) ou routes/api.php (para APIs) e determinam qual código será executado quando um usuário acessa uma URL específica. Exemplo:

```php
Route::get('/exemplo-de-rota', function () {
    echo "Uma rota sem controller, not good!";
});
```

O controller é uma classe responsável por organizar a lógica da aplicação, separando as regras de negócio das rotas. Em vez de definir toda a lógica diretamente nas rotas, os controllers agrupam funcionalidades relacionadas, tornando o código mais limpo e modular. 
A convenção de nomenclatura para controllers segue o padrão PascalCase, onde o nome deve ser descritivo, no singular e sempre terminar com "Controller", como `ProdutoController` ou `UsuarioController`. Vamos criar o LivroController com o seguinte comando que gera automaticamente o arquivo correspondente dentro de `app/Http/Controllers`:

```php
php artisan make:controller LivroController
```

A seguir criamos a rota `livros` e a apontamos para o controller `LivroController`, importando anteriormente o namespace `App\Http\Controllers\LivroController`. O namespace é uma forma de organizar classes, funções e constantes para evitar conflitos de nomes em projetos grandes. Ele permite agrupar elementos relacionados dentro de um mesmo escopo, facilitando a reutilização e manutenção do código.

```php
use App\Http\Controllers\LivroController;
Route::get('/livros', [LivroController::class,'index']);
```

A camada View é responsável por exibir a interface da aplicação, separando a lógica de apresentação da lógica de negócio (controller). Ela utiliza o Blade, uma linguagem de templates que permite criar páginas dinâmicas de forma eficiente. As views ficam armazenadas na pasta `resources/views` e podem ser retornadas a partir de um controller usando return `view('nome_da_view')`.

```php
mkdir resources/views/livros
touch resources/views/livros/index.blade.php
```

No controller:

```php
public function index(){
  return view('livros.index');
}
```

Conteúdo mínimo de index.blade.php:

```html
<!DOCTYPE html>
<html>
    <head>
        <title>Livros</title>
    </head>
    <body>
        Memórias de um Sargento de Milícias<br>
        O Primo Basílio<br>
        Memórias Póstumas de Brás Cubas<br>
        A Hora da Estrela<br>
    </body>
</html>
```

O Model é uma representação de uma tabela no banco de dados e é responsável pela interação com os dados dessa tabela. Ele encapsula a lógica de acesso e manipulação dos dados, permitindo realizar operações como inserção, atualização, exclusão e leitura de registros de forma simples e intuitiva. O Laravel usa o Eloquent ORM (Object-Relational Mapping) para mapear os dados do banco de dados para objetos PHP, o que permite que você trabalhe com as tabelas como se fosse uma classe de objetos.

Criando o model chamado Livro:

```bash
php artisan make:model Livro -m
```

As migrations são uma forma de versionar e gerenciar o esquema do banco de dados, permitindo criar, alterar e remover tabelas de forma controlada e rastreável. Elas funcionam como um histórico de mudanças no banco de dados, ajudando a manter o controle de versões entre diferentes ambientes de desenvolvimento e produção.

Cada migration é uma classe PHP que define as operações a serem realizadas no banco de dados. As migrations são armazenadas na pasta `database/migrations`. As migrations tornam o processo de gerenciamento do banco de dados mais organizado e flexível, principalmente em projetos com múltiplos desenvolvedores. Vamos colocar três colunas para o model `Livro`: titulo, autor e ano.

```php
$table->string('titulo');
$table->string('autor');
$table->integer('ano');
```

Depois da modificação na migration, aplicá-la no banco de dados: `php artisan migrate`.

{: .note-title }
>tinker
>
>O comando `php artisan tinker` nos permite digitar comandos PHP e ver imediatamente o resultado, como se estivesse dentro da sua aplicação Laravel, ou seja, executamos comandos PHP diretamente dentro do contexto da aplicação, de forma prática e rápida.

Usando o tinker, vamos cadastrar dois livros:
```php
$livro = new \App\Models\Livro;
$livro->titulo = "Memórias de um Sargento de Milícias";
$livro->autor = "Manuel Antônio de Almeida";
$livro->ano = 1853;
$livro->save();

$livro = new \App\Models\Livro;
$livro->titulo = "O Primo Basílio";
$livro->autor = "Eça de Queiroz";
$livro->ano = 1878;
$livro->save();
```

Se quisermos conferir diretamente no banco de dados os livros cadastrados, saímos do tinker com Ctrl+C e acessamos o banco com sqlite:

```sql
sqlite3 database/database.sqlite
.tables
SELECT * FROM livros;
.quit
```

Conferido que os livros foram cadastrados no banco de dados, na view da index podemos listar os livros cadastrados:

```php
use App\Models\Livro;

public function index(){
  return view('livros.index',[
    'livros' => Livro::all()
  ]);
}
```

No blade index.blade.php, listamos os livros:
{% raw %}
```php
<ul>
    @foreach($livros as $livro)
        <li>{{ $livro->titulo }}, por <i>{{ $livro->autor }}</i> em {{ $livro->ano }}</li>
    @endforeach
</ul>
```
{% endraw %}

Por fim, podemos criar um comando no artisan que automatiza o cadastro de livros a partir de alguma lógica que podemos desenvolver. 

```php
php artisan make:command ImportaLivros
```

O comando acima criará o arquivo `app/Console/Commands/ImportaLivros.php`, o qual temos que mudar o `$signature` e implementar a lógica do comando:

```php
protected $signature = 'livros:importar';

public function handle()
{
    $livro = new \App\Models\Livro;
    $livro->titulo = "A Hora da Estrela";
    $livro->autor = "Clarice Lispector";
    $livro->ano = 1977;
    $livro->save();
}
```

Ao rodarmos no terminal o comando `php artisan livros:importar` o livro da Clarice será cadastrado. Essa é um implementação simples (e inútil, pois o mesmo livro é sempre cadastrado repetidamente), mas a ideia é que qualquer lógica pode ser implementada no `handle()` para cadastro de muitos livros a partir de uma fonte externa, como, por exemplo, uma lista de livros oriunda de um arquivo csv. 


## Exercício 1 - Importação de Dados e Estatísticas com Laravel

**Objetivo**: Criar um sistema básico em Laravel para importar dados de um arquivo CSV e exibir estatísticas desses dados em uma view.

[https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv](https://raw.githubusercontent.com/mwaskom/seaborn-data/master/exercise.csv)

1) Criar o Model e a Migration:

- Crie um model chamado `Exercise` com uma migration correspondente.
- Na migration, defina os campos necessários com base nas colunas do arquivo `exercise.csv`
- Execute a migration para criar a tabela no banco de dados.

2) Criar um `Command` para Importação

- Crie um comando `exercise:importar`.
- No método `handle()`, implemente a lógica para ler o arquivo `exercise.csv` e salvar os dados no banco de dados usando o model `Exercise`.
- Dica 1: Para zerar os registros a cada importação, pode-se usar o comando `\App\Models\Livros::truncate()` no começo do método `handle()`.
- Dica 2: Você pode usar a classe `League\Csv\Reader` (disponível via Composer) para facilitar a leitura do CSV.

3) Criar estatísticas básicas sobre os dados

- Criar o controller `ExerciseController` com um método chamado `stats`.
- Defina uma rota `exercises/stats` que aponte para o método `stats`.
- No método `stats`, calcule as média aritmética da coluna pulse para os casos rests, walking e running, conforme tabela abaixo.
- Passe esses dados para uma view chamada `resources/views/exercises/stats.blade.php` e monte finalmente a tabela com html.

Exemplo de saída:

|  exercise.csv| rest  | walking   | running |
|--------------|-------|-----------|---------|
|  Qtde linhas |  XX   |     XX    |   XXX   | 
|  Média Pulse |  XX   |     XX    |   XXX   |

# Dia 2

## CRUD

CRUD é um acrônimo para as quatro operações básicas utilizadas na manipulação de dados em sistemas web: Create (Criar), Read (Ler), Update (Atualizar) e Delete (Excluir). Essas operações interagem com bancos de dados, permitindo, por exemplo, que usuários possam cadastrar novas informações, visualizar registros existentes, modificar dados já salvos e remover registros.

### Create

São geralmente necessárias duas rotas para salvar um registro em uma operação CRUD porque o processo é dividido em duas etapas: exibir o formulário e processar os dados enviados. A rota GET serve para exibir o formulário de criação e a rota POST serve para processar os dados enviados pelo formulário no controller:

```php
Route::get('/livros/create', [LivroController::class,'create']);
Route::post('/livros', [LivroController::class,'store']);
```

Para mostrar o formulário html usamos o método *create* :

```php
public function create(){
    return view('livros.create');
}
```

Formulário html será `touch resources/views/livros/create.blade.php` com o seguinte conteúdo:

```php
<form method="POST" action="/livros">
    @csrf
    Título: <input type="text" name="titulo">
    Autor: <input type="text" name="autor">
    Ano: <input type="text" name="ano">
    <button type="submit">Enviar</button>
</form>
```

Por fim o método store, que salva no banco de dados o cadastro do livro:

```php
public function store(Request $request){
    $livro = new Livro;
    $livro->titulo = $request->titulo;
    $livro->autor = $request->autor;
    $livro->ano = $request->ano;
    $livro->save();
    return redirect('/livros');
}
```

### Read

Já implementamos uma forma de acessar os livros em forma de listagem com o método index, podemos implementar outra forma de acesso individual para cada livro. Rota para acesso ao registro de um livro específico:

```php
Route::get('/livros/{livro}', [LivroController::class,'show']);
```

Respectivo controller:
```php
public function show(Livro $livro){
    return view('livros.show',[
        'livro' => $livro
    ]);
}
```

Criamos um blade para a rota show `touch resources/views/livros/show.blade.php` com o seguinte conteúdo:

{% raw %}
```php
Título: {{ $livro->titulo }} <br>
Autor: <i>{{ $livro->autor }}</i> <br>
Ano de publicação: {{ $livro->ano }} <br>
<a href="/livros">Voltar</a>
```
{% endraw %}

No index.blade.php podemos criar um link para o `show` de cada livro:

{% raw %}
```php
<a href="/livros/{{ $livro->id}}">{{ $livro->titulo }}</a>
```
{% endraw %}

### Update

Novamente precisamos de duas rotas para atualizar um registro, uma para exibir o formulário e outra para processar os dados enviados.

```php
Route::get('/livros/{livro}/edit', [LivroController::class,'edit']);
Route::post('/livros/{livro}', [LivroController::class,'update']);
```

Implementação no controller:
```php
public function edit(Livro $livro){
    return view('livros.edit',[
        'livro' => $livro
    ]);
}

public function update(Request $request, Livro $livro){
    $livro->titulo = $request->titulo;
    $livro->autor = $request->autor;
    $livro->ano = $request->ano;
    $livro->save();
    return redirect("/livros/{$livro->id}");
}
```

Criando o blade para edição:

```php
touch resources/views/livros/edit.blade.php
```

Html para edição no `edit.blade.php`:
{% raw %}
```php
<form method="POST" action="/livros">
    @csrf
    Título: <input type="text" name="titulo" value="{{ $livro->titulo }}">
    Autor: <input type="text" name="autor" value="{{ $livro->autor }}">
    Ano: <input type="text" name="ano" value="{{ $livro->ano }}">
    <button type="submit">Enviar</button>
</form>
```
{% endraw %}

Vamos colocar o botão para edição no blade `show.blade.php`:

{% raw %}
```php
Título: {{ $livro->titulo }} <br>
Autor: <i>{{ $livro->autor }}</i> <br>
Ano de publicação: {{ $livro->ano }} <br>
<a href="/livros/{{ $livro->id }}/edit">Editar</a> <br>
<a href="/livros">Voltar</a>
```
{% endraw %}

### Delete

Rota para delete:
```php
Route::delete('/livros/{livro}', [LivroController::class,'destroy']);
```

Controller para delete:
```php
public function destroy(Livro $livro)
{
    $livro->delete();
    return redirect('/livros');
}
```

Botão html para delete que podemos colocar no blade do `show.blade.php`:
{% raw %}
```php
<form action="/livros/{{ $livro->id }} " method="post">
    @csrf
    @method('delete')
    <button type="submit" onclick="return confirm('Tem certeza?');">Apagar</button> 
</form>
```
{% endraw %}


## Exercício 2

1. Criar um CRUD completo para cadastro de livros: [https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv](https://github.com/zygmuntz/goodbooks-10k/blob/master/samples/books.csv). Dica: use outra instância de Laravel para não confundir com o `Model` livro que já estamos usando ao longo do texto. 
2. Criar uma rotina de importação, conforme feito no exercício 1, para importação do csv: [https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv](https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv) (esse é o completo!)
3. Criar rota, controller e view que vai mostrar: 

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

Podemos usar a função `old('titulo')` nos formulários, que nesse caso
verifica se há input na sessão para o campo `titulo`:

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
php artisan make:migration change_isbn_column_in_livros  --table=livros
{% endhighlight %}

Alterando a coluna `isbn` de string para integer na migration acima:
{% highlight php %}
$table->integer('isbn')->change();
{% endhighlight %}

Aplique a mudança no banco de dados:
{% highlight bash %}
php artisan migrate
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

No LivroRequest também deixaremos esse campo como opcional: `'preco'  => 'nullable'`. 

Queremos que o usuário digite, por exemplo, `12,50`, mas guardaremos
`12.5`. Quando quisermos mostrar o valor, vamos fazer a operação
inversa. Poderíamos fazer esse tratamento diretamente no controller,
mas também podemos usar `mutators` através no model do livro:

{% highlight php %}
use Illuminate\Database\Eloquent\Casts\Attribute;

protected function preco(): Attribute
{
    return Attribute::make(
        get: fn($value) => number_format($value, 2, ',', ''),
        set: fn($value) => str_replace(',','.',$value)
    );
}
{% endhighlight %}


## Exercício 3

Esse exercíco é referente ao arquivo: [https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/country_data/Brazil.csv](https://github.com/owid/covid-19-data/blob/master/public/data/vaccinations/country_data/Brazil.csv)

1. Criar model, migration, CRUD, e uma lógica de importação do csv (pode ser uma rota e controller). Na migration defina os campos total_vaccinations e	people_vaccinated como string. Importe o csv.
2. Faça uma migration de alteração para alterar total_vaccinations e people_vaccinated para inteiro
3. Faça um mutator para mostrar o campo date com o formato brasileiro dd/mm/yyyy e outro mutator para salvá-lo commo yyyy-mm-dd (lembre-se que o formulário deve receber dd/mm/yyyy)
4. Implemente o FormRequest garantindo que seja digitado dd/mm/yyyy, além implementar as outras validações
5. Corriga seus formulários para sempre conterem a função old()


<!--
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



# Dia 4

## Testes automatizados com Dusk

Dusk é uma ferramenta de teste automatizado que permite escrever testes de navegador.

Execute o seguinte comando para adicionar o Laravel Dusk como uma dependência de desenvolvimento:

{% highlight php %}
composer require laravel/dusk --dev
php artisan dusk:install
{% endhighlight %}

O diretório tests/Browser será criado automaticamente e um arquivo de configuração para o Dusk.

Você terá um arquivo .env.dusk.local com as configurações específicas para o ambiente de teste Dusk. Copie o arquivo .env para .env.dusk.local e ajuste conforme necessário.

Você pode criar um novo teste de navegador usando o Artisan:

{% highlight php %}
php artisan dusk:make LivroCrudTest
{% endhighlight %}

Isso criará um novo arquivo de teste em tests/Browser/LivroCrudTest.php

Visita a página de criação de livros, preenche o formulário e verifica se o livro foi criado corretamente:
{% highlight php %}
public function testCreateLivro()
{
    $this->browse(function (Browser $browser) {
        $browser->visit('/livros/create')
                ->type('title', 'Meu Novo Post')
                ->type('content', 'Este é o conteúdo do meu novo post.')
                ->press('Salvar')
                ->assertPathIs('/posts')
                ->assertSee('Meu Novo Post')
                ->assertSee('Este é o conteúdo do meu novo post.');
    });
}
{% endhighlight %}


Para executar seus testes, use o seguinte comando:
{% highlight php %}
php artisan dusk
{% endhighlight %}

Cria um livro diretamente no banco de dados, visita a página de detalhes do livro e verifica se as informações estão corretas:
{% highlight php %}
public function testReadPost()
{
    $post = Post::create([
        'title' => 'Post Existente',
        'content' => 'Este é um post existente.',
    ]);

    $this->browse(function (Browser $browser) use ($post) {
        $browser->visit('/posts/' . $post->id)
                ->assertSee('Post Existente')
                ->assertSee('Este é um post existente.');
    });
}
{% endhighlight %}

Cria um livro, visita a página de edição, atualiza os dados e verifica se as mudanças foram salvas:
{% highlight php %}
public function testUpdatePost()
{
    $post = Post::create([
        'title' => 'Post Atualizável',
        'content' => 'Este é um post que será atualizado.',
    ]);

    $this->browse(function (Browser $browser) use ($post) {
        $browser->visit('/posts/' . $post->id . '/edit')
                ->type('title', 'Post Atualizado')
                ->type('content', 'Este é o conteúdo atualizado do post.')
                ->press('Salvar')
                ->assertPathIs('/posts/' . $post->id)
                ->assertSee('Post Atualizado')
                ->assertSee('Este é o conteúdo atualizado do post.');
    });
}
{% endhighlight %}

Cria um livro, executa a ação de deleção e verifica se o livro foi removido da lista.
{% highlight php %}
public function testDeletePost()
{
    $post = Post::create([
        'title' => 'Post Deletável',
        'content' => 'Este é um post que será deletado.',
    ]);

    $this->browse(function (Browser $browser) use ($post) {
        $browser->visit('/posts')
                ->assertSee('Post Deletável')
                ->press('#delete-post-' . $post->id) // Supondo que existe um botão de deleção com este ID
                ->assertPathIs('/posts')
                ->assertDontSee('Post Deletável');
    });
}
{% endhighlight %}


# Dia 5 (Em construção)

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

-->
