# Echo

Create an Echo project via:

```bash
stoke init echo
```

Echo is a minimalist, high-performance HTTP framework for Go.

## Prompts

- **Project name**: directory name for the project
- **Go module name**: e.g. `github.com/user/myapp` (defaults to project name)

## Generated files

    myapp/
    ├── stoke.toml
    ├── go.mod
    ├── main.go                    # Echo entry point
    └── handlers/
        └── hello.go               # sample handlers

## Dependencies

- `github.com/labstack/echo/v4` (installed via `go get`)

## Default settings

- **Port**: `8080`
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Echo + stoke!"}`
  - `GET /hello/:name` → `{"message": "Hello, {name}!"}`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8080/`

## Customization

- Change port: edit `e.Start(":8080")` in `main.go`
- Add handlers: create files in `handlers/` and register in `main.go`
- Add middleware: use `e.Use(...)` in `main.go`