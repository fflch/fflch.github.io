<?php

namespace Tests\Browser;

use Illuminate\Foundation\Testing\DatabaseMigrations;
use Laravel\Dusk\Browser;
use Tests\DuskTestCase;
use App\Models\Livro;

class LivroCrudTest extends DuskTestCase
{
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
}
