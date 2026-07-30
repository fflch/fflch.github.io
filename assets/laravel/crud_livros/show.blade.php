@extends('laravel-usp-theme::master')

@section('content')

Título: {{ $livro->titulo }} <br>
Autor: <i>{{ $livro->autor }}</i> <br>
Ano de publicação: {{ $livro->ano }} <br>
<a href="/livros">Voltar</a>
<a href="/livros/{{ $livro->id }}/edit">Editar</a> <br>

<form action="/livros/{{ $livro->id }} " method="post">
    @csrf
    @method('delete')
    <button type="submit" onclick="return confirm('Tem certeza?');">Apagar</button> 
</form>
@endsection

