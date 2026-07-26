<p align="center">
  <img src="docs/images/logo.png" alt="stoke" width="400">
</p>

<h2 align="center">Build, run, and scaffold projects in multiple languages.</h2>

Supports Python, Java, C, C++, Go, JavaScript, and TypeScript. Includes project scaffolding for Spring Boot, FastAPI, Flask, Django, and 12 Go/JavaScript/TypeScript web framework templates (Gin, Echo, Fiber, Chi, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono).

## Installation

### Windows (recommended for beginners)
Download the installer from [Releases](https://github.com/dvdsvds/stoke/releases/latest). Python is bundled — no prerequisites.

### pip (for developers)
```bash
pip install stoke-build
```
Requires Python 3.11 or higher.

## Quick Start

```bash
mkdir myapp
cd myapp
stoke init
stoke build
stoke run
```

## Features
- **Multi-language** — Python, Java, C, C++, Go, JavaScript, TypeScript with a single stoke.toml
- **Language installation** — install Python/JDK/gcc/Go/Node.js via `stoke install`
- **Project scaffolding** — `stoke init <type>` for Spring Boot, FastAPI, Flask, Django, Gin, Echo, Fiber, Chi, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono
- **Python environments** — venv or conda
- **Watch mode and hot-reload** for all languages
- **Build profiles** — debug/release and custom compile profiles for C/C++
- **Reproducible builds** via lock files
- **Auto IDE integration** (VSCode, IntelliJ, Eclipse)

## Documentation

Full documentation: [https://dvdsvds.github.io/stoke/](https://dvdsvds.github.io/stoke/)

Also available in the repo:
- [English README](./docs/README_en.md)
- [한국어 README](./docs/README_ko.md)

## License

MIT