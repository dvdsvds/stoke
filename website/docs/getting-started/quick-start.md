# Quick Start

This guide walks you through creating and building your first stoke project.

## Create a new project

Use `stoke init` to scaffold a new project interactively:

```bash
mkdir myapp
cd myapp
stoke init
```

The wizard will ask:

- Project name
- Language (Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript)
- Version requirements
- Dependencies

It generates:

- `stoke.toml` — project configuration
- `src/` — source directory with a hello-world file

## Build

```bash
stoke build
```

Output:
Building 'myapp' (cpp)...
Using cpp compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp

Build artifacts land in `.stoke/`.

## Run

```bash
stoke run
```

Output:
Running: ...\myapp.exe
Hello from stoke!

## Watch mode

Auto-rebuild on file changes:

```bash
stoke watch
```

Press Ctrl+C to stop.

## Hot-reload

Rebuild and restart the process automatically:

```bash
stoke hot-reload
```

Useful for servers or long-running processes.

## Language-specific quick starts

### Python

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "python"
python_version = "3.12"
entry = "src/main.py"

[targets.myapp.deps]
requests = "*"
```

```bash
stoke build     # Creates venv, installs deps
stoke run       # Runs src/main.py
```

### Java

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "java"
java_version = "25"
sources = ["src/main/java/**/*.java"]
main_class = "com.example.Main"
```

```bash
stoke build     # Compiles .java files
stoke run       # Runs main_class
```

### C

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "c"
sources = ["src/**/*.c"]
```

```bash
stoke build     # Compiles + links
stoke run       # Runs the executable
```

### C++

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]
```

```bash
stoke build
stoke run
```

### Go

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "go"
```

```bash
stoke build     # go build
stoke run       # runs the compiled binary
```

### Rust

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "rust"
```

```bash
stoke build     # cargo build --release
stoke run       # runs the compiled binary
```

### Kotlin

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "kotlin"
java_version = "21"
```

```bash
stoke build     # gradlew build -x test
stoke run       # gradlew run (needs the application plugin)
```

### C#

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "csharp"
```

```bash
stoke build     # dotnet build
stoke run       # runs the built binary
```

### Ruby

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "ruby"
entry = "src/main.rb"
```

```bash
stoke build     # bundle install (if Gemfile exists)
stoke run       # ruby src/main.rb (or bundle exec ruby)
```

### PHP

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "php"
entry = "src/main.php"
```

```bash
stoke build     # composer install (if composer.json exists)
stoke run       # php src/main.php
```

### JavaScript

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "javascript"
entry = "src/main.js"
```

```bash
stoke build     # npm install (if package.json exists)
stoke run       # node src/main.js
```

### TypeScript

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "typescript"
entry = "src/main.ts"
```

```bash
stoke build     # npm install
stoke run       # runs src/main.ts via tsx
```

## Next steps

- [Commands reference](../commands/overview.md)
- [`stoke.toml` reference](../configuration/stoke-toml.md)
- Language guides: [Python](../languages/en/python.md), [Java](../languages/en/java.md), [C/C++](../languages/en/cpp.md), [Go](../languages/en/go.md), [Rust](../languages/en/rust.md), [Kotlin](../languages/en/kotlin.md), [C#](../languages/en/csharp.md), [Ruby](../languages/en/ruby.md), [PHP](../languages/en/php.md), [JavaScript](../languages/en/javascript.md), [TypeScript](../languages/en/typescript.md)