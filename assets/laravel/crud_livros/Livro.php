<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Casts\Attribute;

class Livro extends Model
{
    protected function preco(): Attribute
    {
        return Attribute::make(
            get: fn($value) => number_format($value, 2, ',', ''),
            set: fn($value) => str_replace(',','.',$value)
        );
    }
}
