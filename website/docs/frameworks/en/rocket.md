# Rocket

Create a Rocket project via:

```bash
stoke init rocket
```

Rocket is an ergonomics-focused web framework for Rust.

## Prompts

- **Project name**: directory name for the project

## Generated files

    myapp/
    ├── stoke.toml
    ├── Cargo.toml
    └── src/
        └── main.rs           # Rocket entry point

## Dependencies

- `rocket` `0.5`

## Default settings

- **Port**: `8000` (Rocket's default)
- **Endpoints**:
  - `GET /` → `Hello from Rocket + stoke!`
  - `GET /hello/<name>` → `Hello, {name}!`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8000/`

## Customization

- Change port: add a `Rocket.toml` with `[default] port = <port>`, or set the `ROCKET_PORT` env var
- Add routes: add functions annotated with `#[get(...)]` and register them in `routes![...]`
- Add state/fairings: use `.manage(...)` / `.attach(...)` on `rocket::build()`
