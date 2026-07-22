# Framework scaffolding

stoke generates ready-to-run projects for popular frameworks with a single command:

```bash
stoke init spring-boot
stoke init fastapi
stoke init flask
stoke init django
stoke init gin
stoke init echo
stoke init fiber
stoke init chi
```

Each command prompts for basic settings (project name, language version, environment type where applicable) and generates the project structure with sample code.

## Available frameworks

### Java

| Command | Framework |
| --- | --- |
| `stoke init spring-boot` | Spring Boot (via Spring Initializr) |

### Python

| Command | Framework |
| --- | --- |
| `stoke init fastapi` | FastAPI + uvicorn |
| `stoke init flask` | Flask + Jinja2 templates |
| `stoke init django` | Django (full project + app) |

### Go

| Command | Framework |
| --- | --- |
| `stoke init gin` | Gin — popular, fast HTTP framework |
| `stoke init echo` | Echo — minimalist, high performance |
| `stoke init fiber` | Fiber — Express-style API |
| `stoke init chi` | Chi — lightweight router using stdlib |

## What's generated

Each framework page below documents the exact files, dependencies, and default settings.

**Java:**
- [Spring Boot](spring-boot.md)

**Python:**
- [FastAPI](fastapi.md)
- [Flask](flask.md)
- [Django](django.md)

**Go:**
- [Gin](gin.md)
- [Echo](echo.md)
- [Fiber](fiber.md)
- [Chi](chi.md)

## After scaffolding

**Python frameworks** use the same workflow:

```bash
stoke build     # Create venv/conda env, install deps
stoke run       # Start the server
```

**Go frameworks** use the same workflow:

```bash
stoke build     # go build
stoke run       # Start the server
```

**Spring Boot** uses Maven (not stoke) after scaffolding:

```bash
cd myapp
mvnw spring-boot:run    # Linux/macOS
mvnw.cmd spring-boot:run  # Windows
```