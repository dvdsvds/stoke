# stoke

Build, run, and scaffold projects in multiple languages
[← Back to main README](../README.md) · [한국어](./README_ko.md)

## Overview

`stoke.toml` manages virtual environments, dependencies, IDE integration, and reproducible builds
Build, run, and scaffold Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript projects with the same interface
Supports project scaffolding for Spring Boot, FastAPI, Flask, Django, and 20 other Go/Rust/Kotlin/C#/Ruby/PHP/JavaScript/TypeScript web frameworks

## Features

- **Multi-language support** — unified management for Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript (12 languages, one `stoke.toml`)
- **Language installation** — install Python/JDK/gcc/Go/Node.js via `stoke install --language=X` (Rust/Kotlin/C#/Ruby/PHP delegate to their own installers — rustup, SDKMAN-style JDKs, the dotnet installer, rbenv/rvm, etc.)
- **Framework scaffolding** — Spring Boot, FastAPI, Flask, Django, Gin, Echo, Fiber, Chi, Actix Web, Axum, Rocket, Ktor, Spring Boot (Kotlin), ASP.NET Core, Sinatra, Slim, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono
- **Python environments** — choose between venv or conda
- **Automatic dependency management** — pip, Maven Central, vcpkg for the languages stoke manages directly; Cargo/Gradle/NuGet/Bundler/Composer/npm handle their own for the rest
- **Version pinning for team consistency** — every language now has a pin mechanism (see [Version pinning](#version-pinning-for-team-consistency) below)
- **Private registry / mirror support** — point toolchain installs and Java's Maven dependency downloads at an internal mirror, with optional Basic Auth (see [Private registries and mirrors](#private-registries-and-mirrors))
- **Build cache** — content-hash based cache invalidation (works correctly across machines/CI, unlike mtime-based caches) plus an optional shared/remote cache for C/C++ and Java (see [Build cache](#build-cache))
- **Parallel multi-target builds** — `stoke build --all` builds every target in `stoke.toml` concurrently
- **Multi-target projects** — `stoke init`, run again inside an existing project, adds a new target instead of asking you to hand-edit `stoke.toml`
- **Automatic IDE integration** — auto-generated config files for VSCode, IntelliJ, Eclipse
- **Watch mode + Hot-reload** — auto rebuild on file change, restart running process
- **Build profiles** — debug/release and custom profiles (compile flags, defines, compiler) for C/C++
- **Reproducible builds** — lock file for team-wide version consistency
- **Incremental builds** — skip unchanged files via a content-hash cache
- **Interactive and non-interactive initialization** — `stoke init` for humans, `stoke init --language=X --yes` for CI/onboarding scripts

## Installation

### Windows (recommended for beginners)
Download the installer from [Releases](https://github.com/dvdsvds/stoke/releases/latest). Python is bundled — no prerequisites.

### pip (for developers)
```bash
pip install stoke-build
```
Requires Python 3.11 or higher for the pip method.

## Quick Start

```bash
mkdir myapp
cd myapp
stoke init
stoke build
stoke run
```

## Supported languages

| Language | Build tool stoke delegates to | Version pinning |
| --- | --- | --- |
| Python | pip / venv / conda (own dependency resolution + lock) | `python_version` in `stoke.toml`, enforced against detected installs |
| Java | `javac` directly (Maven Central for deps, no Maven build) | `java_version` in `stoke.toml`, enforced against detected JDKs |
| C | gcc/clang/MSVC directly, own header-dependency tracking | `c_standard` in `stoke.toml` |
| C++ | gcc/clang/MSVC directly, own header-dependency tracking | `cpp_standard` in `stoke.toml` |
| Go | `go build` / `go run` | optional pin via `go.mod`'s `go`/`toolchain` directives (read by the Go toolchain itself) |
| Rust | `cargo build --release` / run | optional `rust-toolchain.toml` (read by rustup) |
| Kotlin | Gradle Wrapper (`gradlew`) or system `gradle` | `java_version` in `stoke.toml`, enforced via `-Dorg.gradle.java.home` |
| C# | `dotnet build` / `dotnet run` | optional `global.json` (read by dotnet CLI) |
| Ruby | Bundler + `ruby` (`bundle exec ruby` if Gemfile present) | optional `.ruby-version` (read by rbenv/rvm/asdf/chruby) |
| PHP | Composer + `php` | optional `composer.json` `require.php` constraint (enforced by `composer install`) |
| JavaScript | Node.js (`npm install` + `node <entry>`) | optional pin via `.nvmrc` + `package.json`'s `engines.node` |
| TypeScript | Node.js + tsx (compile+run in one step) | optional pin via `.nvmrc` + `package.json`'s `engines.node` |

C/C++ dependency management uses vcpkg. Python/Java use stoke's own lock file (`stoke.lock`). All other languages defer entirely to their own ecosystem's lock file (`Cargo.lock`, `package-lock.json`, `Gemfile.lock`, `composer.lock`, `go.sum`, Gradle's own resolution).

## Commands

### Project management

| Command | Description |
| --- | --- |
| `stoke init` | Interactive project initialization. Run again inside an existing project to add a new target instead of overwriting. |
| `stoke init <framework>` | Scaffold a framework project directly (see [Framework scaffolding](#framework-scaffolding)) |
| `stoke init --language=<lang> [--version] [--name] [--env-type] [--lock-mode] [--vcpkg] [--yes]` | Non-interactive init for CI/onboarding scripts — no prompts |
| `stoke build [target]` | Build target (defaults to the first target in `stoke.toml` if omitted) |
| `stoke build --all` | Build every target in `stoke.toml`, in parallel |
| `stoke build --force` | Full rebuild ignoring cache |
| `stoke build --debug` / `--release` / `--profile=<name>` | Build with a specific profile (C/C++) |
| `stoke run [target]` | Run the built target |
| `stoke watch [target]` | Auto rebuild on file change |
| `stoke hot-reload [target]` | Rebuild + restart running process |
| `stoke clean [target]` | Delete build artifacts |
| `stoke clean --all` | Full reset including lock file |
| `stoke ide-sync` | Regenerate VSCode/Eclipse/IntelliJ config files; also manages workspace-level IDE files |

### Language tools

| Command | Description |
| --- | --- |
| `stoke python list` | Installed Python interpreters |
| `stoke java list` | Installed JDKs |
| `stoke c list` | Installed C compilers (gcc) |
| `stoke cpp list` | Installed C++ compilers (g++) |

Rust/Kotlin/C#/Ruby/PHP toolchains are detected via whatever's already on `PATH` — there's no `stoke <lang> list` for them; Kotlin reuses Java's JDK detection.

### Tool management

| Command | Description |
| --- | --- |
| `stoke install vcpkg` | Install vcpkg to `~/.stoke/tools/vcpkg/` |
| `stoke uninstall vcpkg` | Remove vcpkg |
| `stoke install --language=<lang> --version=<ver> [--base-url=<url>]` | Install a language toolchain (`python`, `java`, `c`, `cpp`, `go`, `nodejs`; default version: `latest`) |
| `stoke install --language=<lang> --list [--base-url=<url>]` | List available versions for a language |
| `stoke uninstall --language=<lang> [--version=<ver>]` | Remove an installed toolchain |

`--base-url` (or the `STOKE_VERSION_API_BASE` env var) points these at an internal mirror instead of stoke's default endpoint — see [Private registries and mirrors](#private-registries-and-mirrors).

### Framework scaffolding

`stoke init <framework>` creates a ready-to-run project for the given framework:

| Language | Frameworks |
| --- | --- |
| Python | `fastapi`, `flask`, `django` |
| Java | `spring-boot` |
| Go | `gin`, `echo`, `fiber`, `chi` |
| Rust | `actix-web`, `axum`, `rocket` |
| Kotlin | `ktor`, `spring-boot-kotlin` |
| C# | `aspnet-core` |
| Ruby | `sinatra` |
| PHP | `slim` |
| JavaScript | `express`, `fastify` |
| TypeScript | `nextjs`, `nestjs`, `vite`, `nuxt`, `sveltekit`, `hono` |

Rails and Laravel are deliberately not offered — both start via a CLI subcommand (`bin/rails server`, `php artisan serve`) rather than running an entry script directly, which doesn't fit stoke's run model. Sinatra/Slim were chosen instead because they do fit it.

### C/C++ library management (vcpkg)

| Command | Description |
| --- | --- |
| `stoke vcpkg install <library>` | Install library (latest) |
| `stoke vcpkg install <library> --version=X` | Install specific version |
| `stoke vcpkg remove <library>` | Remove library |
| `stoke vcpkg list` | List installed libraries |
| `stoke vcpkg version` | Show vcpkg version |

## Configuration examples

### Python

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "python"
python_version = "3.12"
sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.myapp.deps]
requests = "2.31.0"
fastapi = ">=0.100.0"
```

### Java

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "java"
java_version = "21"
sources = ["src/**/*.java"]
main_class = "com.example.Main"

[targets.myapp.deps]
"com.google.code.gson:gson" = "2.10.1"
```

### C

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "c"
c_standard = "c17"
sources = ["src/**/*.c"]
```

### C++

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "cpp"
cpp_standard = "c++17"
sources = ["src/**/*.cpp"]

[targets.myapp.deps]
fmt = "latest"
```

On Windows, set `compiler = "msvc"` on a profile to build with `cl.exe` (Visual Studio's own toolchain) instead of gcc/clang — vcpkg dependencies resolve against the `x64-windows` triplet automatically:

```toml
[profiles.debug]
compiler = "msvc"
```

### Go

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "go"
```

Dependencies are managed via `go.mod`, not `stoke.toml`. `stoke init` optionally pins a `go_version` into `go.mod`'s `go`/`toolchain` directives.

### Rust

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "rust"
```

Dependencies are managed via `Cargo.toml`. `stoke init` optionally writes `rust-toolchain.toml` to pin the toolchain version (rustup reads it automatically).

### Kotlin

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "kotlin"
java_version = "21"
```

Dependencies are managed via `build.gradle.kts`. `java_version` is enforced — stoke resolves a matching JDK and passes it to Gradle via `-Dorg.gradle.java.home`.

### C#

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "csharp"
```

Dependencies (NuGet) are managed via the `.csproj`. `stoke init` optionally writes `global.json` to pin the .NET SDK version (dotnet CLI reads it automatically).

### Ruby

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "ruby"
entry = "src/main.rb"
```

Dependencies are managed via Bundler's `Gemfile` (`bundle exec ruby` is used automatically if a `Gemfile` is present). `stoke init` optionally writes `.ruby-version` (read by rbenv/rvm/asdf/chruby).

### PHP

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "php"
entry = "src/main.php"
```

Dependencies are managed via Composer's `composer.json`. `stoke init` can optionally write a `require.php` version constraint into `composer.json`, enforced by `composer install` itself.

### JavaScript

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "javascript"
entry = "src/main.js"
```

Dependencies are managed via `package.json` (installed with `npm install` on `stoke build`). `stoke init` optionally pins a Node version into `.nvmrc` and `package.json`'s `engines.node`.

### TypeScript

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "typescript"
entry = "src/main.ts"
```

Runs via `tsx`. Dependencies are managed via `package.json`, same Node version pinning as JavaScript above.

## Version pinning for team consistency

- **Python/Java**: `python_version`/`java_version` in `stoke.toml`, checked against installed toolchains at build time.
- **C/C++**: `c_standard`/`cpp_standard` in `stoke.toml`.
- **Kotlin**: `java_version` in `stoke.toml` — stoke resolves a matching JDK and passes it to Gradle via `-Dorg.gradle.java.home`, failing loudly if none match.
- **Rust**: optional `rust-toolchain.toml` — rustup reads it automatically.
- **C#**: optional `global.json` — dotnet CLI reads it automatically.
- **Ruby**: optional `.ruby-version` — rbenv/rvm/asdf/chruby read it automatically.
- **PHP**: optional `composer.json` `require.php` constraint — enforced by `composer install`.
- **Go**: optional pin patched into `go.mod`'s `go` directive (minimum version, enforced by `go build` itself) and `toolchain` directive (exact version — Go's own toolchain manager auto-downloads it when `GOTOOLCHAIN=auto`, the default since Go 1.21).
- **JavaScript/TypeScript**: optional `node_version` pin, written to `.nvmrc` (read by nvm/fnm) and `package.json`'s `engines.node`. A soft pin like Ruby's — `npm install` warns on a mismatch but doesn't block by default (deliberately not paired with `.npmrc`'s `engine-strict=true`, which would also strictly check every dependency's own `engines` field).

All of the optional pins (Rust, C#, Ruby, PHP, Go, JavaScript, TypeScript) are prompted for during `stoke init` — leave the prompt blank to skip pinning. stoke doesn't enforce any of them itself; each one is a native file that the language's own toolchain manager already knows how to read.

## Private registries and mirrors

For networks that only whitelist specific internal hosts, both toolchain installs and Java's dependency downloads can be redirected to an internal mirror:

```bash
# stoke install --language=X --version=Y (toolchain downloads + version listing)
stoke install --language=python --version=3.12 --base-url=https://internal-mirror.company.com/stoke-versions
# or set once for the whole org/CI:
export STOKE_VERSION_API_BASE=https://internal-mirror.company.com/stoke-versions

# stoke build (Java's Maven dependency downloads)
export STOKE_MAVEN_REPO_URL=https://internal-mirror.company.com/maven2
stoke build
```

Both have been verified against Sonatype Nexus (a `raw` hosted repository for the version JSON, and Nexus's built-in `maven-central` proxy for Java deps).

**Authenticated mirrors** are supported for both, via HTTP Basic Auth (credentials go in a header, never the URL):

```bash
export STOKE_MAVEN_USER=ci-user
export STOKE_MAVEN_PASSWORD=***          # for stoke build (Java)
export STOKE_VERSION_API_USER=ci-user
export STOKE_VERSION_API_PASSWORD=***    # for stoke install
```

If unset, no `Authorization` header is sent — anonymous mirrors keep working exactly as before.

This covers `stoke install` (toolchain download) and Java's project-dependency download. Every other language's project dependencies already respect their own ecosystem's native mirror/registry config transparently (pip.conf, `.npmrc`, NuGet.config, `.cargo/config.toml`, Bundler/Composer config, vcpkg registries) — nothing stoke-specific needed there.

## Build cache

- **Content-hash invalidation (all cached languages)** — `.stoke/cache.json` invalidates on a file's SHA-256 content hash rather than mtime/size, so a fresh checkout on a different machine (new mtimes, same content) correctly reuses the cache instead of always missing.
- **Remote/shared cache (C/C++, Java)** — set `STOKE_REMOTE_CACHE_DIR` to any directory reachable from multiple machines (network share, NAS, mapped drive) and `stoke build` fetches/uploads compiled objects there instead of a cache-server protocol. C/C++ caches per compiled `.o` file (with a header-content manifest verified on every hit); Java caches per-target (`javac` batches its whole compile into one invocation, so there's no 1:1 file→output mapping to cache per-file). A missing/unreachable/misconfigured cache dir fails open — it never breaks a build, only skips the speedup.
- **Scope** — C/C++ and Java compilation only. Python has no real compile step to cache. Rust/Kotlin/C#/Ruby/PHP/Go/JS/TS delegate to their own build tools (Cargo, Gradle, dotnet, etc.), which have their own separate caching outside stoke's cache module entirely.

## Pre/post-build hooks

Any target can declare `pre_build`/`post_build` — lists of shell commands run before/after the language-specific build step, for every language:

```toml
[targets.myapp]
language = "python"
pre_build = ["echo starting build"]
post_build = ["cp dist/myapp ./release/myapp"]
```

Commands run via the shell (so pipes/env vars/multiple args work), in declared order, for `stoke build`, `stoke build --all`, `stoke watch`, and `stoke hot-reload` alike. A non-zero exit from any `pre_build` command aborts before the language build runs; a non-zero `post_build` command fails the overall build too.

## Plugin system

An external pip package can add a new language or `stoke init` scaffold without touching stoke's own source, via two entry point groups:

```toml
# plugin package's pyproject.toml
[project.entry-points."stoke.languages"]
mylang = "my_package.stoke_plugin:MYLANG_PLUGIN"

[project.entry-points."stoke.frameworks"]
my-framework = "my_package.stoke_plugin:cmd_init_my_framework"
```

- `stoke.languages` — the entry point resolves to a `stoke.plugins.LanguagePlugin` (an adapter factory plus the source file extensions to watch). Once installed, `stoke build`/`run`/`watch`/`hot-reload` dispatch to it exactly like a built-in language for any target with that `language` name in `stoke.toml`.
- `stoke.frameworks` — the entry point resolves to a zero-argument callable, same contract as the built-in framework handlers (e.g. `cmd_init_fastapi`): it does its own prompting/file-writing and is responsible for producing a working `stoke.toml` + source tree.

A `stoke.languages` plugin only wires up build/run/watch — it doesn't get an interactive `stoke init` wizard entry automatically. To also support `stoke init` for a brand-new language, register a `stoke.frameworks` entry point too that writes the `stoke.toml` (with `language = "<name>"`) itself, the same pattern already used internally for Gin/Echo/Fiber/Chi/Actix Web/etc.

## Lock file modes

- **`commit`** — `stoke.lock` at project root, committed to git (team reproducibility)
- **`local`** — `.stoke/lock.toml`, gitignored (per-developer)

## Dependency version syntax

Only Python, Java, and C/C++ have a `[targets.<name>.deps]` table in `stoke.toml` — every other language manages dependencies entirely through its own native manifest (`Cargo.toml`, `build.gradle.kts`, `.csproj`/NuGet, `Gemfile`, `composer.json`, `package.json`), so there's nothing to configure on the stoke side beyond the config examples above.

### Python (pip specifier)

- `"2.31.0"` — exact version
- `">=2.0.0"`, `"<3.0.0"` — version range
- `"*"` or `""` — any version

### Java (Maven coordinates)

- `"groupId:artifactId" = "version"`
- Example: `"com.google.code.gson:gson" = "2.10.1"`

### C/C++ (vcpkg)

- `"latest"` — latest version (default)
- `"10.2.1"` — specific version

## IDE integration

### Python

- `.vscode/settings.json` — Python interpreter path

### Java

- `.classpath`, `.project` — Eclipse, VSCode Java extension
- `pom.xml` — IntelliJ IDEA, Maven-based IDEs
- `.vscode/settings.json` — referenced libraries

### C / C++

- `compile_commands.json` — clangd, VSCode C/C++ extension, CLion
- `.vscode/c_cpp_properties.json` — VSCode C/C++ extension

### Go / Rust / Kotlin / C# / Ruby / PHP / JavaScript / TypeScript

No stoke-managed IDE files yet — these rely on their own editor tooling out of the box (`gopls`, `rust-analyzer`, the Kotlin/IntelliJ plugin, OmniSharp/the C# extension, Solargraph, Intelephense, built-in TS/JS language services).

### Workspace (multiple projects)

`stoke ide-sync` generates `<folder>.code-workspace` at the workspace root.

Open via `File > Open Workspace from File` in VSCode. Each project is recognized as an independent root

## How it works

When you run `stoke build`:

1. Parse `stoke.toml` and determine target(s) (`--all` builds every target, in parallel)
2. Language-specific processing:
   - Python: create venv → install pip dependencies → syntax check
   - Java: detect JDK → download Maven dependencies (optionally through a mirror) → compile with `javac`, restoring/populating the build cache
   - C/C++: detect compiler → install vcpkg dependencies → compile and link with `gcc`/`g++`, restoring/populating the build cache
   - Go: detect `go` toolchain (honoring any `go.mod` version pin) → `go build`
   - Rust: `cargo build --release`, honoring `rust-toolchain.toml` if present
   - Kotlin: resolve a matching JDK (`java_version`) → `gradlew`/`gradle` build, scoped to the right (sub)project
   - C#: `dotnet build`, honoring `global.json` if present, against the right `.csproj`
   - Ruby: `bundle exec ruby` if a `Gemfile` is present, otherwise `ruby` directly
   - PHP: `composer install` if `composer.json` is present (also enforces any PHP version constraint), then `php`
   - JavaScript/TypeScript: detect Node.js (honoring `.nvmrc`/`engines.node` if pinned) → `npm install` (if `package.json` exists) → run via `node`/`tsx`
3. Generate IDE integration files (`.classpath`, `pom.xml`, `compile_commands.json`, etc.) for Python/Java/C/C++
4. Manage `.gitignore` automatically
5. Save lock file (only on change)
6. Save cache (`.stoke/cache.json`, plus the remote cache directory if `STOKE_REMOTE_CACHE_DIR` is set)

## Python Project Configuration

### Specifying Entry File

The `entry` field in `stoke.toml` specifies the Python file to run. Default is `src/main.py`.

To change the file name or location, edit `stoke.toml` directly:

```toml
[targets.myapp]
entry = "src/myapp/main.py"        # Custom location
# entry = "src/custom_main.py"     # Custom filename
```

### Project Structure Convention

Python requires explicit paths to import modules from subfolders.

**Folder structure**:
src/
├── main.py
└── computer/
├── init.py
└── hardware/
├── init.py
└── cpu.py

**Import in main.py**:
```python
from computer.hardware.cpu import CPU
```

**Note**:
- Each subfolder needs `__init__.py` (empty file works)
- Short names (`from cpu import CPU`) won't work. Full path is required.

## Known limitations

- No macOS/Linux native installer yet (pip works, but isn't verified end-to-end)
- No CMake/Meson integration for C/C++ — stoke has its own simple build model, so large/generated C/C++ build graphs don't fit
- Plugin-based languages don't get an automatic interactive `stoke init` wizard entry (see "Plugin system" above)
- Rust, Kotlin, C#, Ruby, PHP are the newest languages — command construction and templates are verified, but not yet battle-tested against large real-world projects in each ecosystem
- No inter-target dependency graph — `stoke build --all` treats every target as independent
- Rails and Laravel scaffolds are intentionally omitted (see [Framework scaffolding](#framework-scaffolding))

See [`FEATURES.md`](../FEATURES.md) at the repo root for the full, current status writeup (what's verified, open gaps, and whether stoke is a fit for larger organizations).

## Roadmap

- **v0.1** — Python builds (venv, dependencies, syntax check, incremental builds)
- **v0.2** — Watch mode, hot-reload
- **v0.3** — Java support (JDK detection, Maven Central, IDE integration)
- **v0.4** — C/C++ support (gcc/g++, watch, hot-reload, IDE integration)
- **v0.5** — vcpkg integration, tool management, multi-root workspace
- **v0.6** — C/C++ build improvements (header dependency tracking, parallel compilation, automatic IDE integration)
- **v0.7** — Build profile system (debug/release, custom profiles, clang support)
- **v0.8** — Korean CLI help messages (STOKE_LANG env var), internal refactoring
- **v1.0** — Language installation
  - CLI: `stoke install --language=X --version=Y`
  - Custom version API (GitHub Pages)
  - Python, Java, C/C++ support
- **v1.1** — Go language support (install, build, run, uninstall), Go framework scaffolding (Gin, Echo, Fiber, Chi)
- **v1.2** — Node.js installation support
- **v1.3** — JavaScript and TypeScript support, 8 web frameworks (Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono)
- **v1.4** — Rust, Kotlin, C#, Ruby, PHP support (12 languages, 24 frameworks total); non-interactive `stoke init --language=X` for CI/onboarding; version pinning for the 5 new languages plus real `java_version` enforcement for Kotlin; private-registry/mirror support (including authentication) for toolchain installs and Java's Maven dependencies; content-hash build cache invalidation plus a remote/shared cache (`STOKE_REMOTE_CACHE_DIR`) for C/C++ and Java; parallel multi-target builds (`stoke build --all`); `stoke init` can add a target to an existing project; Go/Rust/Kotlin/C# adapters fixed to build each target independently instead of always rebuilding the whole project root
- **v1.5** — Version pinning for Go (`go.mod` `go`/`toolchain` directives) and JavaScript/TypeScript (`.nvmrc` + `package.json` `engines.node`)

## License

MIT
