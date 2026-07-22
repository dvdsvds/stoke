# Go

stoke supports Go projects using the standard `go build` and `go run` tooling.

## Requirements

- Go 1.20 or higher (recommended: 1.26.5 or latest)
- Install via `stoke install --language=go --version=<version>`

## Configuration

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "go"
```

That's it. Go handles its own dependency management via `go.mod`.

## How it works

- `stoke build` runs `go build -o <output>` in the project root
- `stoke run` executes the compiled binary
- Dependencies are managed by Go itself via `go.mod` and `go.sum`

## Example

Create a new Go project:

```bash
mkdir myapp
cd myapp
stoke init
```

Select `Go` from the language menu. stoke will:

- Create `stoke.toml`
- Run `go mod init myapp`
- Generate `main.go` with a hello-world example

Then:

```bash
stoke build
stoke run
```

## Framework scaffolding

For web frameworks, use:

```bash
stoke init gin      # Gin — popular, fast HTTP framework
stoke init echo     # Echo — minimalist, high performance
stoke init fiber    # Fiber — Express-style API
stoke init chi      # Chi — lightweight router using stdlib
```

See [Frameworks](../frameworks/en/overview.md) for details.

## Notes

- stoke builds the main package (`.`) not `./...` — this avoids conflicts with subpackages like `handlers/`
- Go binaries include the runtime; no separate installation needed to run
- Cross-compilation via `GOOS=linux GOARCH=amd64 stoke build` (Go env vars work)