# Chi

Create a Chi project via:

```bash
stoke init chi
```

Chi is a lightweight, idiomatic router for Go, built on `net/http`.

## Prompts

- **Project name**: directory name for the project
- **Go module name**: e.g. `github.com/user/myapp` (defaults to project name)

## Generated files

    myapp/
    ├── stoke.toml
    ├── go.mod
    ├── main.go                    # Chi entry point
    └── handlers/
        └── hello.go               # sample handlers

## Dependencies

- `github.com/go-chi/chi/v5` (installed via `go get`)

## Default settings

- **Port**: `8080`
- **Middleware**: Logger (built-in)
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Chi + stoke!"}`
  - `GET /hello/{name}` → `{"message": "Hello, {name}!"}`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8080/`

## Customization

- Change port: edit `http.ListenAndServe(":8080", r)` in `main.go`
- Add handlers: create files in `handlers/` and register in `main.go`
- Add middleware: use `r.Use(...)` in `main.go`

## Notes

Chi follows Go's `net/http` conventions, so handlers use `func(w http.ResponseWriter, r *http.Request)`. This makes it easy to use existing Go HTTP libraries and middleware.