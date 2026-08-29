# Axum

Create an Axum project via:

```bash
stoke init axum
```

Axum is a Tokio-based web framework built by the Tokio team.

## Prompts

- **Project name**: directory name for the project

## Generated files

    myapp/
    ├── stoke.toml
    ├── Cargo.toml
    └── src/
        └── main.rs           # Axum entry point

## Dependencies

- `axum` `0.7`
- `tokio` `1` (with the `full` feature)

## Default settings

- **Port**: `8080`
- **Endpoints**:
  - `GET /` → `Hello from Axum + stoke!`
  - `GET /hello/:name` → `Hello, {name}!`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8080/`

## Customization

- Change port: edit `TcpListener::bind("127.0.0.1:8080")` in `src/main.rs`
- Add routes: add `.route("/path", get(handler))` calls to the `Router`
- Add middleware: use `.layer(...)` on the `Router`
