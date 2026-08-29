# Slim Framework

Create a Slim Framework project via:

```bash
stoke init slim
```

Slim is a lightweight PSR-7 micro-framework for PHP.

## Prompts

- **Project name**: directory name for the project

## Generated files

    myapp/
    ├── stoke.toml
    ├── composer.json
    └── public/
        └── index.php          # Slim entry point

## Dependencies

- `slim/slim` `^4.0`
- `slim/psr7` `^1.6` (PSR-7 implementation)

## Default settings

- **Endpoints**:
  - `GET /` → `Hello from Slim + stoke!`
  - `GET /hello/{name}` → `Hello, {name}!`

## Run

Slim needs PHP's built-in development server — it doesn't start a server on its own the way Sinatra does, so `stoke run` alone isn't enough:

```bash
cd myapp
composer install               # if not already run during scaffolding
php -S localhost:8000 -t public
```

Open `http://localhost:8000/`

!!! note
    `stoke build` (composer install) and `stoke run` still work — `stoke run` just executes `public/index.php` once via the CLI SAPI and exits, since there's no request to route without an HTTP server in front of it. Use `php -S` above for actual development.

## Customization

- Add routes: add `$app->get(...)` / `$app->post(...)` calls in `public/index.php`
- Add middleware: use `$app->add(...)`
- Split routes into their own files as the project grows (common Slim convention: a `routes/` directory required from `index.php`)
