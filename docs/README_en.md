# stoke

Build, run, and scaffold projects in multiple languages
[← Back to main README](../README.md) · [한국어](./README_ko.md)

## Overview

`stoke.toml` manages virtual environments, dependencies, IDE integration, and reproducible builds
Build, run, and scaffold Python, Java, C, and C++ projects with the same interface
Supports project scaffolding for Spring Boot, FastAPI, Flask, and Django

## Features

- **Multi-language support** — unified management for Python, Java, C, C++
- **Language installation** — install Python/JDK/gcc via `stoke install`
- **Framework scaffolding** — Spring Boot, FastAPI, Flask, Django
- **Python environments** — choose between venv or conda
- **Automatic dependency management** — pip, Maven Central, vcpkg integration
- **Automatic IDE integration** — auto-generated config files for VSCode, IntelliJ, Eclipse
- **Watch mode + Hot-reload** — auto rebuild on file change, restart running process
- **Reproducible builds** — lock file for team-wide version consistency
- **Incremental builds** — skip unchanged files via mtime cache
- **Interactive initialization** — `stoke init` for project setup

## Installation

```bash
pip install stoke-build
```

Requires Python 3.11 or higher

## Quick Start

```bash
mkdir myapp
cd myapp
stoke init
stoke build
stoke run
```

## Commands

### Project management

| Command | Description |
| --- | --- |
| `stoke init` | Interactive project initialization (Python, Java, C, C++) |
| `stoke build [target]` | Build target |
| `stoke build --force` | Full rebuild ignoring cache |
| `stoke run [target]` | Run the built target |
| `stoke watch [target]` | Auto rebuild on file change |
| `stoke hot-reload [target]` | Rebuild + restart running process |
| `stoke clean [target]` | Delete build artifacts |
| `stoke clean --all` | Full reset including lock file |
| `stoke ide-sync` | Manage workspace-level IDE files |

### Language tools

| Command | Description |
| --- | --- |
| `stoke python list` | Installed Python interpreters |
| `stoke java list` | Installed JDKs |
| `stoke c list` | Installed C compilers (gcc) |
| `stoke cpp list` | Installed C++ compilers (g++) |

### Tool management

| Command | Description |
| --- | --- |
| `stoke install vcpkg` | Install vcpkg to `~/.stoke/tools/vcpkg/` |
| `stoke uninstall vcpkg` | Remove vcpkg |

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

## Lock file modes

- **`commit`** — `stoke.lock` at project root, committed to git (team reproducibility)
- **`local`** — `.stoke/lock.toml`, gitignored (per-developer)

## Dependency version syntax

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

### Workspace (multiple projects)

`stoke ide-sync` generates `<folder>.code-workspace` at the workspace root.

Open via `File > Open Workspace from File` in VSCode. Each project is recognized as an independent root

## How it works

When you run `stoke build`:

1. Parse `stoke.toml` and determine target
2. Language-specific processing:
   - Python: create venv → install pip dependencies → syntax check
   - Java: detect JDK → download Maven dependencies → compile with `javac`
   - C/C++: detect compiler → install vcpkg dependencies → compile and link with `gcc`/`g++`
3. Generate IDE integration files (`.classpath`, `pom.xml`, `compile_commands.json`, etc.)
4. Manage `.gitignore` automatically
5. Save lock file (only on change)
6. Save cache (`.stoke/cache.json`)

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

## License

MIT