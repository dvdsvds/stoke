# Actix-web

Create an Actix-web project via:

```bash
stoke init actix-web
```

Actix-web is a mature, high-performance web framework for Rust.

## Prompts

- **Project name**: directory name for the project

## Generated files

    myapp/
    ├── stoke.toml
    ├── Cargo.toml
    └── src/
        └── main.rs           # Actix-web entry point

## Dependencies

- `actix-web` `4` (declared in `Cargo.toml`, fetched by Cargo on build)

## Default settings

- **Port**: `8080`
- **Endpoints**:
  - `GET /` → `Hello from Actix-web + stoke!`
  - `GET /hello/{name}` → `Hello, {name}!`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8080/`

## Customization

- Change port: edit `.bind(("127.0.0.1", 8080))` in `src/main.rs`
- Add routes: add functions annotated with `#[get(...)]` / `#[post(...)]` and register them with `.service(...)`
- Add middleware: use `.wrap(...)` on the `App`
