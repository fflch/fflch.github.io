mkdir -p app/Http/Requests
mkdir -p app/Console/Commands
mkdir -p resources/views/livros
mkdir -p tests/Browser

# .env
curl -L https://fflch.github.io/assets/laravel/crud_livros/env -o .env

# Migration
curl -L https://fflch.github.io/assets/laravel/crud_livros/2026_07_30_131403_create_livros_table.php \
    -o database/migrations/2026_07_30_131403_create_livros_table.php

# Models
curl -L https://fflch.github.io/assets/laravel/crud_livros/Livro.php \
    -o app/Models/Livro.php

curl -L https://fflch.github.io/assets/laravel/crud_livros/User.php \
    -o app/Models/User.php

# Controller
curl -L https://fflch.github.io/assets/laravel/crud_livros/LivroController.php \
    -o app/Http/Controllers/LivroController.php

curl -L https://fflch.github.io/assets/laravel/crud_livros/IndexController.php \
    -o app/Http/Controllers/IndexController.php

# Form Request
curl -L https://fflch.github.io/assets/laravel/crud_livros/LivroRequest.php \
    -o app/Http/Requests/LivroRequest.php

# Artisan Command
curl -L https://fflch.github.io/assets/laravel/crud_livros/ImportaLivros.php \
    -o app/Console/Commands/ImportaLivros.php

# Views
curl -L https://fflch.github.io/assets/laravel/crud_livros/home.blade.php \
    -o resources/views/home.blade.php

curl -L https://fflch.github.io/assets/laravel/crud_livros/index.blade.php \
    -o resources/views/livros/index.blade.php

curl -L https://fflch.github.io/assets/laravel/crud_livros/create.blade.php \
    -o resources/views/livros/create.blade.php

curl -L https://fflch.github.io/assets/laravel/crud_livros/edit.blade.php \
    -o resources/views/livros/edit.blade.php

curl -L https://fflch.github.io/assets/laravel/crud_livros/show.blade.php \
    -o resources/views/livros/show.blade.php

# Rotas
curl -L https://fflch.github.io/assets/laravel/crud_livros/web.php \
    -o routes/web.php

# Teste
curl -L https://fflch.github.io/assets/laravel/crud_livros/LivroCrudTest.php \
    -o tests/Browser/LivroCrudTest.php

# Senha Única
docker exec -it cursolaravel composer require uspdev/senhaunica-socialite
docker exec -it cursolaravel php artisan vendor:publish --provider="Uspdev\SenhaunicaSocialite\SenhaunicaServiceProvider" --tag="migrations"
docker exec -it cursolaravel php artisan vendor:publish --provider="Spatie\Permission\PermissionServiceProvider"
docker exec -it cursolaravel php artisan migrate

# dusk
docker exec -it cursolaravel composer require --dev laravel/dusk
docker exec -it cursolaravel php artisan dusk:install
docker exec -it cursolaravel php artisan dusk:chrome-driver

# theme
docker exec -it cursolaravel composer require uspdev/laravel-usp-theme
docker exec -it cursolaravel php artisan vendor:publish --provider="Uspdev\UspTheme\ServiceProvider" --tag=config
docker exec -it cursolaravel php artisan vendor:publish --provider="Uspdev\UspTheme\ServiceProvider" --tag=assets --force

# outras libs
docker exec -it cursolaravel composer require league/csv