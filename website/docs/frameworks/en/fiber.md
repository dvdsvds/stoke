# Fiber

Create a Fiber project via:

```bash
stoke init fiber
```

Fiber is an Express-inspired web framework for Go, built on top of Fasthttp.

## Prompts

- **Project name**: directory name for the project
- **Go module name**: e.g. `github.com/user/myapp` (defaults to project name)

## Generated files

    myapp/
    ├── stoke.toml
    ├── go.mod
    ├── main.go                    # Fiber entry point
    └── handlers/
        └── hello.go               # sample handlers

## Dependencies

- `github.com/gofiber/fiber/v2` (installed via `go get`)

## Default settings

- **Port**: `3000`
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Fiber + stoke!"}`
  - `GET /hello/:name` → `{"message": "Hello, {name}!"}`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:3000/`

## Customization

- Change port: edit `app.Listen(":3000")` in `main.go`
- Add handlers: create files in `handlers/` and register in `main.go`
- Add middleware: use `app.Use(...)` in `main.go`