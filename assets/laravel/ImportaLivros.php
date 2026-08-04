<?php

namespace App\Console\Commands;

use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use App\Models\Livro;
use League\Csv\Reader;

#[Signature('app:importa-livros')]
#[Description('Command description')]
class ImportaLivros extends Command
{
    public function handle(): int
    {
        Livro::truncate();
        $conteudo = file_get_contents('https://fflch.github.io/assets/livros.csv');
        $csv = Reader::createFromString($conteudo);
        $csv->setHeaderOffset(0);

        foreach ($csv->getRecords() as $registro) {
            $livro = new Livro;
            $livro->titulo = $registro['titulo'];
            $livro->autor = $registro['autor'];
            $livro->ano = $registro['ano'];
            $livro->save();
        }
        $this->info('Importação concluída!');
        return self::SUCCESS;
    }
}
