<p align="center">
  <img src="docs/images/logo.png" alt="stoke" width="400">
</p>

<h2 align="center">Build, run, and scaffold projects in multiple languages.</h2>

Supports Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript (12 languages) with a single `stoke.toml`. Includes project scaffolding for Spring Boot, FastAPI, Flask, Django, and 20 other web framework templates across Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript (Gin, Echo, Fiber, Chi, Actix Web, Axum, Rocket, Ktor, ASP.NET Core, Sinatra, Slim, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono).

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
- **Multi-language** — Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript with a single stoke.toml
- **Language installation** — install Python/JDK/gcc/Go/Node.js via `stoke install` (Rust/Kotlin/C#/Ruby/PHP delegate to their own installers)
- **Project scaffolding** — `stoke init <type>` for Spring Boot, FastAPI, Flask, Django, Gin, Echo, Fiber, Chi, Actix Web, Axum, Rocket, Ktor, ASP.NET Core, Sinatra, Slim, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono
- **Python environments** — venv or conda
- **Watch mode and hot-reload** for all languages
- **Build profiles** — debug/release and custom compile profiles for C/C++, including MSVC (`compiler = "msvc"`) alongside gcc/clang on Windows
- **Version pinning** — every language now has a pin mechanism, prompted during `stoke init` (e.g. Go's `go.mod` `go`/`toolchain` directives, Node's `.nvmrc` + `package.json` `engines.node`, Rust's `rust-toolchain.toml`) so every teammate and CI runner builds against the same version
- **Private registry / mirror support** — point toolchain installs and Java's Maven dependency downloads at an internal mirror, with optional Basic Auth
- **Build cache** — content-hash cache invalidation plus a shared/remote cache for C/C++ and Java
- **Parallel multi-target builds** — `stoke build --all`, and `stoke init` can add a target to an existing project
- **Pre/post-build hooks** — `pre_build`/`post_build` shell commands per target, for every language and every build path (`build`, `build --all`, `watch`, `hot-reload`)
- **Reproducible builds** via lock files
- **Auto IDE integration** (VSCode, IntelliJ, Eclipse)

## Documentation

Full documentation: [https://dvdsvds.github.io/stoke/](https://dvdsvds.github.io/stoke/)

Also available in the repo:
- [How To Use guide](./docs/HOW_TO_USE.md) ([한국어](./docs/HOW_TO_USE_KO.md))
- [English README](./docs/README_en.md)
- [한국어 README](./docs/README_ko.md)
- [Full feature status](./FEATURES.md) ([한국어](./FEATURES.ko.md)) — what's verified, known gaps, and whether stoke fits a larger org

## License

MIT