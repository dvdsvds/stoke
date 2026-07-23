# Framework scaffolding

stoke generates ready-to-run projects for popular frameworks with a single command:

```bash
# Java
stoke init spring-boot

# Python
stoke init fastapi
stoke init flask
stoke init django

# Go
stoke init gin
stoke init echo
stoke init fiber
stoke init chi

# JavaScript
stoke init express
stoke init fastify

# TypeScript
stoke init nextjs
stoke init nestjs
stoke init vite
stoke init nuxt
stoke init sveltekit
stoke init hono
```

Each command prompts for basic settings and generates the project structure with sample code.

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

### JavaScript

| Command | Framework |
| --- | --- |
| `stoke init express` | Express — classic Node.js web framework |
| `stoke init fastify` | Fastify — fast, low-overhead framework |

### TypeScript

| Command | Framework |
| --- | --- |
| `stoke init nextjs` | Next.js — React full-stack |
| `stoke init nestjs` | NestJS — Angular-style backend |
| `stoke init vite` | Vite — fast frontend build tool |
| `stoke init nuxt` | Nuxt — Vue full-stack |
| `stoke init sveltekit` | SvelteKit — Svelte full-stack |
| `stoke init hono` | Hono — edge computing framework |

## What's generated

Each framework page below documents the details:

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

**JavaScript:**
- [Express](express.md)
- [Fastify](fastify.md)

**TypeScript:**
- [Next.js](nextjs.md)
- [NestJS](nestjs.md)
- [Vite](vite.md)
- [Nuxt](nuxt.md)
- [SvelteKit](sveltekit.md)
- [Hono](hono.md)

## After scaffolding

**Python, Go, JavaScript frameworks (Express, Fastify)** use the same workflow:

```bash
stoke build
stoke run
```

**Spring Boot** uses Maven:

```bash
mvnw spring-boot:run    # Linux/macOS
mvnw.cmd spring-boot:run  # Windows
```

**TypeScript frameworks (Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono)** use each framework's own commands:

```bash
npm run dev     # Development
npm run build   # Production
```

stoke calls the official scaffolding tools (`create-next-app`, `@nestjs/cli`, `nuxi`, `sv create`, etc.) so you get the latest project templates.