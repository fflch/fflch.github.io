<form method="POST" action="/livros/{{ $livro->id }}">
    @csrf
    @method('PATCH')
    Título: <input type="text" name="titulo" value="{{ old('titulo', $livro->titulo) }}">
    Autor: <input type="text" name="autor" value="{{ old('autor', $livro->autor) }}">
    Ano: <input type="text" name="ano" value="{{ old('ano', $livro->ano) }}">
    <button type="submit">Enviar</button>
</form>
