# Framework scaffolding

stoke generates ready-to-run projects for popular frameworks with a single command:

```bash
stoke init spring-boot
stoke init fastapi
stoke init flask
stoke init django
```

Each command prompts for basic settings (project name, Python/Java version, environment type) and generates the project structure with sample code.

## Available frameworks

| Command | Language | Framework |
| --- | --- | --- |
| `stoke init spring-boot` | Java | Spring Boot (via Spring Initializr) |
| `stoke init fastapi` | Python | FastAPI + uvicorn |
| `stoke init flask` | Python | Flask + Jinja2 templates |
| `stoke init django` | Python | Django (full project + app) |

## What's generated

Each framework page below documents the exact files, dependencies, and default settings.

- [Spring Boot](spring-boot.md)
- [FastAPI](fastapi.md)
- [Flask](flask.md)
- [Django](django.md)

## After scaffolding

All Python frameworks use the same workflow:

```bash
stoke build     # Create venv/conda env, install deps
stoke run       # Start the server
```

Spring Boot uses Maven (not stoke) after scaffolding:

```bash
cd myapp
mvnw spring-boot:run    # Linux/macOS
mvnw.cmd spring-boot:run  # Windows
```