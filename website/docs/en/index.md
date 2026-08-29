<div class="stoke-hero" markdown>

![stoke](../assets/logo-mark.png)

# stoke

**Build, run, and scaffold projects in multiple languages.**

stoke unifies development workflows for Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript. One CLI for building, running, watching, and scaffolding — including popular frameworks like Spring Boot, FastAPI, Flask, Django, Gin, Express, Next.js, Actix-web, Ktor, and ASP.NET Core.

<div class="stoke-cta" markdown>
[Get started](getting-started/installation.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/dvdsvds/stoke){ .md-button }
</div>

</div>

## Features

<div class="grid cards" markdown>

- :material-language-python:{ .lg .middle } **Multi-language**

    ---

    Build Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript projects with the same commands.

- :material-download-box:{ .lg .middle } **Language installation**

    ---

    Install Python/JDK/gcc/Go/Node.js via `stoke install` — no separate setup required.

- :material-rocket-launch:{ .lg .middle } **Framework scaffolding**

    ---

    Spring Boot, FastAPI, Flask, Django, plus web frameworks for Go, JavaScript, TypeScript, Rust, Kotlin, C#, Ruby, and PHP.

- :material-lightning-bolt:{ .lg .middle } **Fast**

    ---

    Incremental compilation with header dependency tracking. Only what changed gets rebuilt.

- :material-file-cog:{ .lg .middle } **Simple**

    ---

    One `stoke.toml` for the whole project — no per-language config files to juggle.

- :material-eye-refresh:{ .lg .middle } **Watch & hot-reload**

    ---

    Auto-rebuild on file changes, with optional process restart for long-running servers.

- :material-application-brackets:{ .lg .middle } **IDE integration**

    ---

    Auto-generates VSCode/Eclipse/IntelliJ configs on every build.

- :material-tune-variant:{ .lg .middle } **Build profiles**

    ---

    Debug/Release/custom profiles with their own flags and defines.

</div>

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
- [Languages](languages/python.md) — language-specific guides
- [Configuration](configuration/stoke-toml.md) — `stoke.toml` reference
- [Advanced](advanced/vcpkg.md) — vcpkg, IDE integration

## Links

- **GitHub**: [github.com/dvdsvds/stoke](https://github.com/dvdsvds/stoke)
- **Releases**: [Latest version](https://github.com/dvdsvds/stoke/releases)
