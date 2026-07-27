# stoke

**Build, run, and scaffold projects in multiple languages.**

stoke unifies development workflows for Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript projects. One command-line interface for building, running, watching, and scaffolding — including popular frameworks like Spring Boot, FastAPI, Flask, Django, Gin, Express, Next.js, Actix-web, Ktor, ASP.NET Core, and more. Configure your project once in `stoke.toml`, and stoke handles compilation, dependency management, IDE integration, and more.

## Features

- **Multi-language**: Build Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript projects with the same commands
- **Language installation**: Install Python/JDK/gcc/Go/Node.js via `stoke install`
- **Framework scaffolding**: Spring Boot, FastAPI, Flask, Django, plus web frameworks for Go, JavaScript, TypeScript, Rust, Kotlin, C#, Ruby, and PHP
- **Python environments**: venv or conda
- **Fast**: Incremental compilation with header dependency tracking
- **Simple**: One `stoke.toml` for the whole project
- **Watch mode**: Auto-rebuild on file changes
- **Hot-reload**: Restart processes on rebuild
- **IDE integration**: Auto-generates VSCode/Eclipse/IntelliJ configs
- **Build profiles**: Debug/Release/custom profiles
- **Dependency management**: pip for Python, Maven for Java, vcpkg for C/C++, go.mod for Go, Cargo for Rust, Gradle for Kotlin, NuGet for C#, Bundler for Ruby, Composer for PHP, npm for JavaScript/TypeScript

## Quick example

Create `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]
```

Build and run:

```bash
stoke build
stoke run
```

That's it.

## Getting Started

- [Installation](getting-started/installation.md) — install stoke on Windows/Linux/macOS
- [Quick Start](getting-started/quick-start.md) — build your first project

## Documentation Sections

- [Commands](commands/overview.md) — build, run, watch, and more
- [Languages](languages/en/python.md) — language-specific guides
- [Configuration](configuration/stoke-toml.md) — `stoke.toml` reference
- [Advanced](advanced/vcpkg.md) — vcpkg, IDE integration

## Links

- **GitHub**: [github.com/dvdsvds/stoke](https://github.com/dvdsvds/stoke)
- **PyPI**: [pypi.org/project/stoke-build](https://pypi.org/project/stoke-build/)
- **Releases**: [Latest version](https://github.com/dvdsvds/stoke/releases)