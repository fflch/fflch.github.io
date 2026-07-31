<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use \Spatie\Permission\Traits\HasRoles;
use \Uspdev\SenhaunicaSocialite\Traits\HasSenhaunica;

class User extends Authenticatable
{
    use HasRoles, HasSenhaunica;
    protected $guard_name = 'senhaunica';
    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
        ];
    }
}
