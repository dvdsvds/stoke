# stoke init

Create a new stoke project interactively.

## Usage

```bash
stoke init
```

Runs an interactive wizard in the current directory.

```bash
stoke init <framework>
```

Skips the wizard and scaffolds a specific framework directly (e.g. `stoke init fastapi`, `stoke init gin`). See [Framework scaffolding](../frameworks/overview.md) for the full list.

## What it does

The wizard asks:

1. **Project name** — defaults to the current folder name
2. **Language** — Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, or TypeScript
3. **Language version** — Python 3.12, Java 25, C11, C++20, etc. (Go/JavaScript/TypeScript have no version prompt at all — they use whatever toolchain is on PATH; Kotlin prompts for a JDK version, reusing the Java detection; Rust/C#/Ruby/PHP prompt for an *optional* toolchain version pin — see [Non-interactive mode](#non-interactive-mode-ci-team-onboarding) and the language pages for what gets generated)
4. **Entry point / main class** — depending on the language
5. **Dependencies** — optional

Then it generates:

- `stoke.toml` — project configuration
- `src/` — source directory
- A hello-world source file

## Example: C++ project
$ mkdir myapp && cd myapp
$ stoke init
Project name [myapp]:
Language [python/java/c/cpp]: cpp
C++ standard [17/20/23] [20]:
Executable name [myapp]:
Install vcpkg for C/C++ library management? [y/N]: n
Created:
stoke.toml
src/main.cpp
Try:
stoke build
stoke run

Generated `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]
cpp_standard = "c++20"
```

## Example: Python project
$ mkdir myapp && cd myapp
$ stoke init
Project name [myapp]:
Language [python/java/c/cpp]: python
Python version [3.10/3.11/3.12/3.13]: 3.12
Entry file [src/main.py]:
Created:
stoke.toml
src/main.py

Generated `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "python"
python_version = "3.12"
entry = "src/main.py"
sources = ["src/**/*.py"]
```

## Example: Java project
$ mkdir myapp && cd myapp
$ stoke init
Project name [myapp]:
Language [python/java/c/cpp]: java
Java version [17/21/25]: 25
Package [com.myapp]:
Main class [Main]:
Created:
stoke.toml
src/main/java/com/myapp/Main.java

Generated `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "java"
java_version = "25"
sources = ["src/main/java/**/*.java"]
main_class = "com.myapp.Main"
```

## Non-interactive mode (CI / team onboarding)

For scripts, CI, or scaffolding tools where prompts aren't an option, pass `--language` and stoke skips the wizard entirely:

```bash
stoke init --language=rust --name=myapp --version=1.75.0 --lock-mode=commit --yes
```

| Flag | Meaning |
| --- | --- |
| `--language` | Required. One of: `python`, `java`, `c`, `cpp`, `go`, `rust`, `kotlin`, `csharp`, `ruby`, `php`, `javascript`, `typescript` |
| `--name` | Project name. Defaults to the current folder name |
| `--version` | Meaning depends on the language (see table below). Omit to use a sensible default |
| `--env-type` | `venv` or `conda`. Python only, defaults to `venv` |
| `--lock-mode` | `commit` or `local`. Defaults to `commit` |
| `--vcpkg` | Install vcpkg if not already present. C/C++ only |
| `--yes` | Overwrite an existing `stoke.toml` without prompting. Without this flag, init fails loudly if `stoke.toml` already exists — safer for scripts than silently clobbering a teammate's config |

`--version` per language:

| Language | `--version` means | Default if omitted |
| --- | --- | --- |
| Python | Python version (e.g. `3.12`) | System's default detected install |
| Java | JDK version (e.g. `21`) | System's default detected install |
| Kotlin | JDK version, written as `java_version` in `stoke.toml` | System's default detected install |
| C | C standard (e.g. `c17`) | `c17` |
| C++ | C++ standard (e.g. `c++20`) | `c++17` |
| Rust | Optional toolchain pin, written to `rust-toolchain.toml` | Not written (no pin) |
| C# | Optional SDK pin, written to `global.json` | Not written (no pin) |
| Ruby | Optional version pin, written to `.ruby-version` | Not written (no pin) |
| PHP | Optional version constraint, written into `composer.json`'s `require.php` | Not written (no pin) |
| Go, JavaScript, TypeScript | Not used | — |

Exit codes are meaningful (`0` success, non-zero failure), so this composes cleanly in onboarding scripts:

```bash
#!/usr/bin/env bash
set -e
mkdir myapp && cd myapp
stoke init --language=python --version=3.12 --lock-mode=commit --yes
stoke build
```

## Version pinning for team consistency

Rust, C#, Ruby, and PHP don't have their own version-manager concept the way Python/Java do in stoke, so `stoke init` can optionally write the ecosystem's own standard pin file — committed to git, it makes every teammate's `stoke build` use (or fail loudly without) the same toolchain version:

- **Rust** → `rust-toolchain.toml` (read automatically by `rustup`)
- **C#** → `global.json` (read automatically by the `dotnet` CLI)
- **Ruby** → `.ruby-version` (read automatically by rbenv/rvm/asdf/chruby)
- **PHP** → `composer.json`'s `require.php` constraint (enforced by `composer install`, which runs as part of `stoke build` once `composer.json` exists)
- **Kotlin** → the existing `java_version` field in `stoke.toml` is enforced by stoke itself: `stoke build`/`stoke run` resolve a matching JDK and pass it to Gradle via `-Dorg.gradle.java.home`, failing with a clear error if no matching JDK is installed

These prompts are optional in the interactive wizard (leave blank to skip) and only apply when `--version` is passed in non-interactive mode.

## After init

Build and run:

```bash
stoke build
stoke run
```

## Related

- [Quick Start](../getting-started/quick-start.md)
- [`stoke.toml` reference](../configuration/stoke-toml.md)