@extends('laravel-usp-theme::master')

@section('content')
<form>
    <input type="text" name="search" value="{{ request('search') }}">
    <button type="submit">Pesquisar</button>
</form>


<h1>Listagem de Livros</h1>
<ul>
    @foreach($livros as $livro)
        <li><a href="/livros/{{ $livro->id}}">{{ $livro->titulo }}</a>, por <i>{{ $livro->autor }}</i> em {{ $livro->ano }}</li>
    @endforeach
</ul>
@endsection
