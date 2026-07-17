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
- Language (Python, Java, C, C++)
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

## Next steps

- [Commands reference](../commands/overview.md)
- [`stoke.toml` reference](../configuration/stoke-toml.md)
- Language guides: [Python](../languages/python.md), [Java](../languages/java.md), [C/C++](../languages/cpp.md)