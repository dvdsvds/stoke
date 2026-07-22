# Gin

Create a Gin project via:

```bash
stoke init gin
```

Gin is a popular, high-performance HTTP web framework for Go.

## Prompts

- **Project name**: directory name for the project
- **Go module name**: e.g. `github.com/user/myapp` (defaults to project name)

## Generated files

    myapp/
    ├── stoke.toml
    ├── go.mod
    ├── main.go                    # Gin entry point
    └── handlers/
        └── hello.go               # sample handlers

## Dependencies

- `github.com/gin-gonic/gin` (installed via `go get`)

## Default settings

- **Port**: `8080`
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Gin + stoke!"}`
  - `GET /hello/:name` → `{"message": "Hello, {name}!"}`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8080/`

## Customization

- Change port: edit `r.Run(":8080")` in `main.go`
- Add handlers: create files in `handlers/` and register them in `main.go`
- Add middleware: use `r.Use(...)` in `main.go`