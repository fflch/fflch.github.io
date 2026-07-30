---
title: Laravel
---
# Dia 1

## Configurando ambiente 

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

[Dockerfile](../assets/laravel/Dockerfile) pronto para usar no contexto USP:
[[include:laravel/Dockerfile]]


[docker-compose.yml](../assets/laravel/docker-compose.yml) pronto para usar no contexto USP:
[[include:laravel/docker-compose.yml]]


Criando a imagem e subindo ambiente:
```bash
docker compose up --build
```

Acessar o laravel criado: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Acessar phpmyadmin criado: [http://127.0.0.1:8081/](http://127.0.0.1:8081/)

Acessar servidor de autenticação USP: [http://auth.local:3141](http://auth.local:3141)


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

O comando `docker exec -it cursolaravel php artisan tinker` nos permite digitar comandos PHP e ver imediatamente o resultado, como se estivesse dentro da sua aplicação Laravel, ou seja, executamos comandos PHP diretamente dentro do contexto da aplicação, de forma prática e rápida.

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

```php
<h1>Listagem de Livros</h1>
<ul>
    @foreach($livros as $livro)
        <li>{{ $livro->titulo }}, por <i>{{ $livro->autor }}</i> em {{ $livro->ano }}</li>
    @endforeach
</ul>
```

### Busca

Inserindo um campo para busca simples no blade:

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

Para rodar os testes, configure no .env (e aproveite coloque no .env.example):

```php
APP_URL=http://cursolaravel
DUSK_DRIVER_URL='http://selenium:4444/wd/hub'
DUSK_START_MAXIMIZED=true
DUSK_HEADLESS_DISABLED=true
```

Criando uma classe do Dusk para inserirmos nosso teste:

```bash
docker exec -it cursolaravel php artisan dusk:make BuscaLivroTest
```

Criando um teste que verifica se na rota /livros existe a frase "Listagem de Livros":

```php
$browser->visit('/livros')
    ->pause(2000)
    ->typeSlowly('search', 'primo', 300)
    ->pause(2000)
    ->press('Pesquisar')
    ->pause(2000)
    ->assertSee('O Primo Basílio');
```

Acessar [http://localhost:7900/](http://localhost:7900/) com senha `secret` e assistir o teste rodando.

Rodar o teste:

```bash
docker exec -it cursolaravel php artisan dusk tests/Browser/BuscaLivroTest.php
```

## Exercício - Importação de Livros

1 - Criar um comando para importar os livros do arquivo csv [livros](../assets/livros.csv) no model Livro. Importante:

- No método `handle()`, implemente a lógica para ler o arquivo `livros.csv` e para cada livro, fazer a inserção;
- Dica 1: Para zerar os registros a cada importação, pode-se usar o comando `\App\Models\Livro::truncate()` no começo do método `handle()`.
- Dica 2: Você pode usar a classe `League\Csv\Reader` (disponível via Composer) para facilitar a leitura do CSV.

2 - Criar teste Dusk para buscar a string "processo" e deverá ter um assert para ver Franz Kafka e um assert not para José de Alencar;

3 - Criar estatísticas básicas sobre os dados importados

- Criar o controller `EstatisticaController` com um método chamado `stats`.
- Defina uma rota `livros/stats` que aponte para o método `stats`.
- No método `stats` apresente uma tabela com a quantidade de livros por ano.

Exemplo de saída (com dados fictícios):

<table class="table">
<thead>
  <tr>
    <th>ano</th>
    <th>quantidade</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>1998</td>
    <td>4</td>
  </tr>
  <tr>
    <td>2000</td>
    <td>7</td>
  </tr>
</tbody>
</table>

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

```php
Título: {{ $livro->titulo }} <br>
Autor: <i>{{ $livro->autor }}</i> <br>
Ano de publicação: {{ $livro->ano }} <br>
<a href="/livros">Voltar</a>
```

No index.blade.php podemos criar um link para o `show` de cada livro:

```php
<a href="/livros/{{ $livro->id}}">{{ $livro->titulo }}</a>
```

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

Vamos colocar o botão para edição no blade `show.blade.php`:

```php
<a href="/livros/{{ $livro->id }}/edit">Editar</a> <br>
```


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

```php
<form action="/livros/{{ $livro->id }} " method="post">
    @csrf
    @method('delete')
    <button type="submit" onclick="return confirm('Tem certeza?');">Apagar</button> 
</form>
```


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
3. Criar um comando, importarfrases, que importa o arquivo csv: [frases](../assets/frases.csv)
4. Criar uma rota `/frasedodia` e o método correspondente que ao ser acessada mostra uma frase aleatória, porém correspondente ao dia da semana. 

Na próxima reunião, cada membro do grupo (estagiários e funcionários) deve apresentar a implementação na TV.

# Dia 3

Instalação do template USP conforme: [https://github.com/uspdev/laravel-usp-theme/](https://github.com/uspdev/laravel-usp-theme/)


Instalação do senhaunica-socialite conforme: [https://github.com/uspdev/senhaunica-socialite](https://github.com/uspdev/senhaunica-socialite)

Configurações para usar o faker:

```bash
APP_URL=http://localhost:8000
SENHAUNICA_KEY=faker
SENHAUNICA_SECRET=faker
SENHAUNICA_CALLBACK_ID=1
SENHAUNICA_ADMINS=111111
SENHAUNICA_DEV="http://auth.local:3141/wsusuario/oauth"
```

## Migration de Alteração

Quando o sistema está produção, você nunca deve alterar uma migration que já foi para o ar, mas sim criar uma migration que altera uma anterior. Por exemplo, se quisermos que adicionar o campo user_id na tabela livros:

```bash
php artisan make:migration add_user_id_to_livros_table --table=livros
```

Nova coluna user_id:

```php
$table->unsignedBigInteger('user_id')->nullable();

$table->foreign('user_id')->references('id')->on('users')->nullOnDelete();
```

Aplique a mudança no banco de dados:
```bash
php artisan migrate
```

No controller, é possível capturar o usuário logado assim: `auth()->user()->id`.

## Validação

### Validação no Controller

Quando estamos dentro de um método do controller, a forma mais rápida de validação é usando `$request->validate`, que validará os campos com as condições que passarmos e caso falhe a validação, automaticamente o usuário é retornado para página de origem com todos inputs que foram enviados na requisição, além da mensagens de erro:

```php
$request->validate([
  'titulo' => 'required',
  'autor' => 'required',
  'ano' => 'required|integer',
]);
```

Podemos usar a função `old('titulo')` nos formulários, que nesse caso verifica se há input na sessão para o campo `titulo`:

```html
Título: <input type="text" name="titulo" value="{{old('titulo')}}">
Autor: <input type="text" name="autor" value="{{old('autor')}}">
Ano: <input type="text" name="ano" value="{{old('ano')}}">
```

### FormRequest

A validação, que muitas vezes será idêntica no store e no update, pode ser delegada para um FormRequest. Crie um FormRequest com o artisan:

```bash
php artisan make:request LivroRequest
```

Esse comando gerou o arquivo `app/Http/Requests/LivroRequest.php`. Como ainda não falamos de permissões, retorne `true` no método
`authorize()`. As validações podem ser implementada em `rules()`.

```php
public function rules(){
    $rules = [
        'titulo' => 'required',
        'autor'  => 'required',
        'ano' => 'required|integer',
    ];
    return $rules;
}
```

## Mutators

Há situações em que queremos fazer um leve processamento antes de salvar um valor no banco de dados e logo após recuperarmos um valor. Vamos adicionar um campo para preço. Já sabemos como criar uma migration de alteração para alterar a tabela livros:

```bash
php artisan make:migration add_preco_column_in_livros --table=livros
```

E adicionamos na nova coluna:
```php
$table->float('preco')->nullable();
```

No LivroRequest também deixaremos esse campo como opcional: `'preco'  => 'nullable'`. 

Queremos que o usuário digite, por exemplo, `12,50`, mas guardaremos `12.5`. Quando quisermos mostrar o valor, vamos fazer a operação inversa. Poderíamos fazer esse tratamento diretamente no controller, mas também podemos usar `mutators` através no model do livro:

```php
use Illuminate\Database\Eloquent\Casts\Attribute;

protected function preco(): Attribute
{
    return Attribute::make(
        get: fn($value) => number_format($value, 2, ',', ''),
        set: fn($value) => str_replace(',','.',$value)
    );
}
```

## Exercício 3

1. No exercício anterior, inserir o usuário no model de frases como nullable, e restringir o cadastro somente para usuários cadastrados, guardando o id do respectivo usuário que está realizando o cadastro;
2. Alterar o Dusk do exercício anterior (frases) para realizar todos os testes com um usuário logado, para isso será necessário criar o usuário durante o teste;
3. Faça uma migration de alteração para adicionar o campo pontuação para a frase (entre 0 e 10 - validação com FormRequest);
4. Faça um mutator converter a virgula, quando existir, para ponto.
5. Corrija seus formulários para sempre conterem a função old()



# Instruções para produção

**1 - Imagem do docker**

Para construção da imagem baseada na tag (versão) criar o arquivo `.github/workflows/docker.yml`:
[Arquivo modelo docker.yml](/assets/files/laravel/docker.yml)

**2 - testes no dusk**

Para rodar os testes no dusk baseado na configuração do docker-compose.yml, criar o arquivo `.github/workflows/dusk.yml`:
[Arquivo modelo dusk.yml](/assets/files/laravel/dusk.yml)
É necessário alterar a variável `SERVICE_NAME` no `dusk.yml` colocando o nome do sistema. 


<!--
Ideias para dia 4:
https://github.com/laravel-shift/blueprint

- Permission customizadas
- Jobs
- Envio de Email
- Relacionamentos
- select
- rule
- replicado
- audit
- stepper
- Upload de arquivos
- Trabalhando com pdf
- Vídeos

models:
  Livro4:
    titulo: string
    autor: string
    ano: integer

controllers:
  Livro4:
    resource: web

config:
  generate_tests: false
-->
