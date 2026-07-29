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

Iremos usar o docker para fazer a instalação;

```bash
mkdir cursolaravel
cd cursolaravel
```

O Composer é um gerenciador de dependências para PHP. Ele permite instalar, atualizar e gerenciar bibliotecas e pacotes de forma simples, garantindo que um projeto tenha todas as dependências necessárias. No Laravel, o Composer é usado para instalar o framework e suas bibliotecas.

```bash
docker run --rm -it \
  -v $(pwd):/app \
  -u $(id -u):$(id -g) \
  composer:latest \
  composer create-project laravel/laravel .
```

[Dockerfile](/assets/files/laravel/Dockerfile) pronto para usar no contexto USP:
```yaml
{% include files/laravel/Dockerfile %}
```

[docker-compose.yml](/assets/files/laravel/docker-compose.yml) pronto para usar no contexto USP:

```yaml
{% include files/laravel/docker-compose.yml %}
```


Criando a imagem e subindo ambiente:
```bash
docker compose up --build
```

Acessar pelo navegador: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

No arquivo .env vamos trocar para mariadb:

```bash
DB_CONNECTION=mariadb
DB_HOST=mariadb
DB_PORT=3306
DB_DATABASE=cursolaravel
DB_USERNAME=cursolaravel
DB_PASSWORD=cursolaravel
```

Recriando tabelas no banco de dados:

```bash
docker exec -it cursolaravel php artisan migrate
```

## MVC 

Uma rota é a forma como o framework define e gerencia URLs para acessar diferentes partes da aplicação. As rotas são configuradas no arquivo routes/web.php (para páginas web) ou routes/api.php (para APIs) e determinam qual código será executado quando um usuário acessa uma URL específica. Exemplo:

```php
Route::get('/rota-sem-controller', function () {
    echo "Uma rota sem controller, not good!";
});
```

O controller é uma classe responsável por organizar a lógica da aplicação, separando as regras de negócio das rotas. Em vez de definir toda a lógica diretamente nas rotas, os controllers agrupam funcionalidades relacionadas, tornando o código mais limpo e modular. 
A convenção de nomenclatura para controllers segue o padrão PascalCase, onde o nome deve ser descritivo, no singular e sempre terminar com "Controller", como `ProdutoController` ou `UsuarioController`. 


```bash
docker exec -it cursolaravel php artisan make:controller MeuPrimeiroController
```

Método do controller:
```bash
public function index(){
    return 'Uma rota com controller, Great!';
}
```

Mesma ideia, mas com controller:
```bash
use App\Http\Controllers\MeuPrimeiroController;
Route::get('/rota-com-controller', [MeuPrimeiroController::class,'index']);
```

Com essa ideia, vamos criar um sistema de cadastro de livros:

```php
docker exec -it cursolaravel php artisan make:controller LivroController
```

A seguir criamos a rota `livros` e a apontamos para o controller `LivroController`, importando anteriormente o namespace `App\Http\Controllers\LivroController`.

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

### Model

O Model é uma representação de uma tabela no banco de dados e é responsável pela interação com os dados dessa tabela.

Criando o model chamado Livro:

```bash
docker exec -it cursolaravel php artisan make:model Livro -m
```

As migrations são uma forma de versionar e gerenciar o esquema do banco de dados, permitindo criar, alterar e remover tabelas de forma controlada e rastreável. 

Cada migration é uma classe PHP que define as operações a serem realizadas no banco de dados. As migrations são armazenadas na pasta `database/migrations`. Vamos colocar três colunas para o model `Livro`: titulo, autor e ano.

```php
$table->string('titulo');
$table->string('autor');
$table->integer('ano');
```

Depois da modificação na migration, aplicá-la no banco de dados: `docker exec -it cursolaravel php artisan migrate`.

### Tinker

{: .note-title }
>tinker
>
>O comando `docker exec -it cursolaravel php artisan tinker` nos permite digitar comandos PHP e ver imediatamente o resultado, como se estivesse dentro da sua aplicação Laravel, ou seja, executamos comandos PHP diretamente dentro do contexto da aplicação, de forma prática e rápida.

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

Na view da index podemos listar os livros cadastrados:

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
<h1>Listagem de Livros</h1>
<ul>
    @foreach($livros as $livro)
        <li>{{ $livro->titulo }}, por <i>{{ $livro->autor }}</i> em {{ $livro->ano }}</li>
    @endforeach
</ul>
```
{% endraw %}


### Busca

No blade, podemos inserir um campo para busca:

```html
<form>
    <input type="text" name="search" value="{{ request('search') }}">
    <button type="submit">Pesquisar</button>
</form>
```

E no controller temos que tratar a busca:

```php
public function index(Request $request){
    if($request->has('search')){
        $livros = Livro::where('titulo','like','%'.$request->search.'%')->get();
    } else {
        $livros = Livro::all();
    }

    return view('livros.index',[
        'livros' => $livros
    ]);
}
```

### Command

Por fim, podemos criar um comando no artisan que automatiza o cadastro de livros a partir de alguma lógica que podemos desenvolver. 

```php
docker exec -it cursolaravel php artisan make:command ImportaLivros
```

O comando acima criará o arquivo `app/Console/Commands/ImportaLivros.php`, o qual temos que mudar o `$signature` e implementar a lógica do comando:

```php
#[Signature('livros:importar')]

public function handle()
{
    $livro = new \App\Models\Livro;
    $livro->titulo = "A Hora da Estrela";
    $livro->autor = "Clarice Lispector";
    $livro->ano = 1977;
    $livro->save();
}
```

Ao rodarmos no terminal o comando `docker exec -it cursolaravel php artisan livros:importar` o livro da Clarice será cadastrado. Essa é um implementação simples (e inútil, pois o mesmo livro é sempre cadastrado repetidamente), mas a ideia é que qualquer lógica pode ser implementada no `handle()` para cadastro de muitos livros a partir de uma fonte externa, como, por exemplo, uma lista de livros oriunda de um arquivo csv.

### Dusk

Os testes com **Laravel Dusk** no nosso contexto tem dois propósitos:

1. **Testar funcionalidades reais do sistema**, simulando a interação de um usuário no navegador.
2. **Servir como documentação funcional**, demonstrando como as principais funcionalidades do sistema devem se comportar.

```bash
docker exec -it cursolaravel composer require --dev laravel/dusk
docker exec -it cursolaravel php artisan dusk:install
docker exec -it cursolaravel php artisan dusk:chrome-driver
```

Para rodar os testes, configure no .env:

```php
APP_URL=http://cursolaravel
DUSK_DRIVER_URL='http://selenium:4444/wd/hub'
DUSK_START_MAXIMIZED=true
DUSK_HEADLESS_DISABLED=true
```

Criando uma classe do Dusk para inserirmos nosso teste:

{% highlight bash %}
docker exec -it cursolaravel php artisan dusk:make BuscaLivroTest
{% endhighlight %}

Criando um teste que verifica se na rota /livros existe a frase "Listagem de Livros":

{% highlight php %}
$browser->visit('/livros')
    ->pause(2000)
    ->typeSlowly('search', 'primo', 300)
    ->pause(2000)
    ->press('Pesquisar')
    ->pause(2000)
    ->assertSee('O Primo Basílio');
{% endhighlight %}

Acessar http://localhost:7900/ com senha secret e assitir.

Rodar o teste:

{% highlight bash %}
docker exec -it cursolaravel php artisan dusk tests/Browser/BuscaLivroTest.php
{% endhighlight %}

## Exercício - Importação de Livros

1 - Criar um comando para importar os livros do arquivo csv [livros](/assets/files/livros.csv) no model Livro. Importante:

- No método `handle()`, implemente a lógica para ler o arquivo `livros.csv` e para cada livro, fazer a inserção;
- Dica 1: Para zerar os registros a cada importação, pode-se usar o comando `\App\Models\Livro::truncate()` no começo do método `handle()`.
- Dica 2: Você pode usar a classe `League\Csv\Reader` (disponível via Composer) para facilitar a leitura do CSV.

2 - Criar teste Dusk para buscar a string "processo" e deverá ter um assert para ver Franz Kafka e um assert not para José de Alencar;

3 - Criar estatísticas básicas sobre os dados importados

- Criar o controller `EstatisticaController` com um método chamado `stats`.
- Defina uma rota `livros/stats` que aponte para o método `stats`.
- No método `stats` apresente uma tabela com a quantidade de livros por ano.

Exemplo de saída (com dados fictícios):

|  ano  | quantidade |
|-------|------------|
|  1998 |  5         | 
|  2001 | 23         |

4 -  No método `stats` apresente uma segunda tabela com a quantidade de livros por autor.

Na próxima reunião, cada membro do grupo (estagiários e funcionários) deve apresentar na TV rapidamente e solução do exercício.


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

Formulário html `resources/views/livros/create.blade.php` com o seguinte conteúdo:

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

Criamos um blade para a rota show `resources/views/livros/show.blade.php` com o seguinte conteúdo:

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
Route::patch('/livros/{livro}', [LivroController::class,'update']);
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
<form method="POST" action="/livros/{{ $livro->id }}">
    @csrf
    @method('PATCH')
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
<a href="/livros/{{ $livro->id }}/edit">Editar</a> <br>
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

Implementação do dusk para testar as operações de CRUD:
```bash
php artisan dusk:make LivroCrudTest
```
Vamos testar sequencialmente as operações:
```php
use App\Models\Livro;
public function test_crud_livros(): void
{
    $this->browse(function (Browser $browser) {
        // Create
        $browser->visit('/livros/create')
            ->typeSlowly('titulo', '2001: Uma odisséia no espaço')
            ->typeSlowly('autor', 'Arthur C. Clarke')
            ->typeSlowly('ano', '1968')
            ->press('Enviar')
            ->assertPathIs('/livros')
            ->assertSee('2001: Uma odisséia no espaço');

        // Read
        $browser->clickLink('2001: Uma odisséia no espaço')
            ->assertSee('Arthur C. Clarke')
            ->assertSee('1968');

        // Update
        $browser->clickLink('Editar')
            ->typeSlowly('titulo', '2001: Uma odisséia no espaço - Edição Revisada')
            ->press('Enviar')
            ->assertSee('2001: Uma odisséia no espaço - Edição Revisada');

        // Delete
        $browser->press('Apagar')
            ->acceptDialog()
            ->assertPathIs('/livros')
            ->assertDontSee('2001: Uma odisséia no espaço - Edição Revisada');
    });
}
```

Rodando o teste:

```bash
docker exec -it cursolaravel php artisan dusk tests/Browser/LivroCrudTest.php
```

## Exercício 2

1. Criar um CRUD completo para o model frases. 
2. Criar uma classe dusk que testa todas funcionalidades do CRUD frases
3. Criar um comando, importarfrases, que importa o arquivo csv: [frases](/assets/files/frases.csv)
4. Criar uma rota `/frasedodia` e o método correspondente que ao ser acessada mostra uma frase aleatória, porém correspondente ao dia da semana. 

Na próxima reunião, cada membro do grupo (estagiários e funcionários) deve apresentar a implementação na TV.

# Dia 3

Instalação do template USP conforme: [https://github.com/uspdev/laravel-usp-theme/](https://github.com/uspdev/laravel-usp-theme/)


Instalação do senhaunica-socialite conforme: [https://github.com/uspdev/senhaunica-socialite](https://github.com/uspdev/senhaunica-socialite)

Configurações para usar o faker:

```
APP_URL=http://localhost:8000
SENHAUNICA_KEY=faker
SENHAUNICA_SECRET=faker
SENHAUNICA_CALLBACK_ID=1
SENHAUNICA_ADMINS=111111
SENHAUNICA_DEV="http://auth.local:3141/wsusuario/oauth"
```

## Migration de Alteração

Quando o sistema está produção, você nunca deve alterar uma migration que já foi
para o ar, mas sim criar uma migration que altera uma anterior. Por exemplo, 
se quisermos que adicionar o campo user_id na tabela livros:

{% highlight bash %}
php artisan make:migration add_user_id_to_livros_table --table=livros
{% endhighlight %}

Nova coluna user_id:

{% highlight php %}
$table->unsignedBigInteger('user_id')->nullable();

$table->foreign('user_id')->references('id')->on('users')->nullOnDelete();
{% endhighlight %}

Aplique a mudança no banco de dados:
{% highlight bash %}
php artisan migrate
{% endhighlight %}

No controller, é possível capturar o usuário logado assim: `auth()->user()->id`.

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
  'ano' => 'required|integer',
]);
{% endhighlight %}

Podemos usar a função `old('titulo')` nos formulários, que nesse caso
verifica se há input na sessão para o campo `titulo`:

{% highlight html %}
{% raw %}
Título: <input type="text" name="titulo" value="{{old('titulo')}}">
Autor: <input type="text" name="autor" value="{{old('autor')}}">
Ano: <input type="text" name="ano" value="{{old('ano')}}">
{% endraw %}
{% endhighlight %}

### FormRequest

A validação, que muitas vezes será idêntica no store e no update, pode ser
delegada para um FormRequest. Crie um FormRequest com o artisan:

{% highlight bash %}
php artisan make:request LivroRequest
{% endhighlight %}

Esse comando gerou o arquivo `app/Http/Requests/LivroRequest.php`. Como
ainda não falamos de permissões, retorne `true` no método
`authorize()`. As validações podem ser implementada em `rules()`.

{% highlight php %}
public function rules(){
    $rules = [
        'titulo' => 'required',
        'autor'  => 'required',
        'ano' => 'required|integer',
    ];
    return $rules;
}
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

1. No exercício anterior, inserir o usuário no model de frases como nullable, e restringir o cadastro somente para usuários cadastrados, guardando o id do respectivo usuário que está realizando o cadastro;
2. Alterar o Dusk do exercício anterior (frases) para realizar todos os testes com um usuário logado, para isso será necessário criar o usuário durante o teste;
3. Faça uma migration de alteração para adicionar o campo pontuação para a frase (entre 0 e 10 - validação com FormRequest);
4. Faça um mutator converter a virgula, quando existir, para ponto.
5. Corriga seus formulários para sempre conterem a função old()



# Instruções para produção


### Imagem do docker

Construção da imagem baseada na tag (versão), ou seja, antes de ir para produção, é necessário fazer uma release:

Criar o arquivo `.github/workflows/docker.yml`:

[Arquivo modelo docker.yml](/assets/files/laravel/docker.yml)




## teste no dusk

Roda os teste no dusk baseado na configuração do docker-compose.yml

Criar o arquivo `.github/workflows/dusk.yml`:

[Arquivo modelo docker.yml](/assets/files/laravel/dusk.yml)

É necessário alterar a variável `SERVICE_NAME` no `dusk.yml` colocando o nome do sistema. 




<!--

## Dusk

Os testes com **Laravel Dusk** no nosso contexto tem dois propósitos:

1. **Testar funcionalidades reais do sistema**, simulando a interação de um usuário no navegador.
2. **Servir como documentação funcional**, demonstrando como as principais funcionalidades do sistema devem se comportar.

Vamos configurar o **em modo assistido**, ou seja, diretamente na sua máquina, pois assim é possível **visualizar o navegador Chrome virtual executando os testes**. Por esse motivo, neste caso **não executamos os testes em container**.

E vamos configurar o **`.github/workflows`** para os testes rodarem automaticamente no **GitHub Actions**, garantindo que falhas nos testes sejam detectadas durante novos commits ou pull requests.

{% highlight bash %}
composer require --dev laravel/dusk
php artisan dusk:install
php artisan dusk:chrome-driver
{% endhighlight %}

Colocar linha `php artisan dusk:chrome-driver --detect` no composer.json:

{% highlight php %}
"scripts": {
    "post-install-cmd": [
        "@php artisan dusk:chrome-driver --detect"
    ]
}
{% endhighlight %}

Criar uma Trait que comunica com o senhaunica-socialite:
{% highlight bash %}
mkdir app/Helpers;
touch app/Helpers/UspdevDuskTrait.php
{% endhighlight %}

Conteúdo da Trait:
{% highlight bash %}
<?php

namespace App\Helpers;

use App\Models\User;
use Spatie\Permission\Models\Permission;

trait UspdevDuskTrait
{
    protected $adminUser;
    protected $commonUser;

    protected function setupAdminAndUser()
    {
        Permission::firstOrCreate(['name' => 'admin', 'guard_name' => 'senhaunica']);
        Permission::firstOrCreate(['name' => 'user', 'guard_name' => 'senhaunica']);

        $this->commonUser = User::firstOrCreate(
            ['email' => 'user@test.com'],
            ['name' => 'Dusk User', 'password' => bcrypt('password')]
        );
        $this->commonUser->givePermissionTo('user', 'senhaunica');

        $this->adminUser = User::firstOrCreate(
            ['email' => 'admin@test.com'],
            ['name' => 'Dusk Admin', 'password' => bcrypt('password')]
        );
        $this->adminUser->givePermissionTo('admin', 'senhaunica');
    }
}
{% endhighlight %}

Criar um arquivo .env.testing.example:

{% highlight bash %}
APP_NAME="Exemplo Dusk"
APP_ENV=testing
APP_KEY=
APP_DEBUG=true
APP_URL=http://127.0.0.1:47800
DUSK_DRIVER_URL=http://localhost:9515

# DB
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=exemplo_dusk
DB_USERNAME=admin
DB_PASSWORD=admin

# Filas
QUEUE_CONNECTION=sync

# Drivers de Performance para Testes
# Usamos 'array' ou 'file' para garantir que os testes não poluam o cache real
CACHE_DRIVER=array
FILESYSTEM_DISK=local

SESSION_DRIVER=file
SESSION_LIFETIME=120

# Configurações de Email (Não envia emails reais durante o teste)
MAIL_MAILER=log

# Dusk
DUSK_START_MAXIMIZED=true
DUSK_HEADLESS_DISABLED=true
{% endhighlight %}


### Rodando os testes

Copie o arquivo de exemplo:

{% highlight bash %}
    cp .env.testing.example .env.testing
{% endhighlight %}

Preparar o ambiente de testes:

{% highlight bash %}
    composer install
    php artisan key:generate --env=testing
    php artisan migrate:fresh --env=testing
    php artisan serve --port=47800 --env=testing
{% endhighlight %}

Durante a execução, o navegador Chrome controlado pelo Laravel Dusk abrirá automaticamente e realizará as interações definidas nos testes.


{% highlight bash %}
    php artisan dusk --env=testing
{% endhighlight %}

Usar a trait criada em app/Helpers:

{% highlight php %}
    use App\Helpers\UspdevDuskTrait;
    class NovoTest  extends DuskTestCase{
        use UspdevDuskTrait;

        protected function setUp(): void
        {
            parent::setUp();
            ...
            $this->setupAdminAndUser(); // cria usuários $this->commonUser e $this->adminUser
        }
    ...
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
