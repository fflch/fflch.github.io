<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Livro;

class LivroController extends Controller
{
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

    public function create(){
        return view('livros.create');
    }

    public function store(Request $request){
        $livro = new Livro;
        $livro->titulo = $request->titulo;
        $livro->autor = $request->autor;
        $livro->ano = $request->ano;
        $livro->save();
        return redirect('/livros');
    }

    public function show(Livro $livro){
        return view('livros.show',[
            'livro' => $livro
        ]);
    }

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

    public function destroy(Livro $livro)
    {
        $livro->delete();
        return redirect('/livros');
    }

}
