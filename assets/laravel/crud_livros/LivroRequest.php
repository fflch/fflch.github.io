<?php

namespace App\Http\Requests;

use Illuminate\Contracts\Validation\ValidationRule;
use Illuminate\Foundation\Http\FormRequest;

class LivroRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(){
        $rules = [
            'titulo' => 'required',
            'autor'  => 'required',
            'ano' => 'required|integer',
        ];
        return $rules;
    }
}
