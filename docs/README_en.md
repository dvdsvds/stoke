# stoke

A multi-language build tool with automatic venv management and reproducible builds.

[← Back to main README](../README.md) · [한국어 문서](./README_ko.md)

## Overview

**stoke** manages virtual environments, dependencies, and reproducible builds through a simple `stoke.toml` configuration file.

> Currently supports Python. Java and C/C++ support is planned.

## Features

- **Automatic venv management** — Creates and reuses virtual environments per target
- **Python version selection** — Detects installed Python versions and lets you pin the one you want
- **Reproducible builds** — Lock file (`stoke.lock`) ensures everyone uses the same Python version and package versions
- **Incremental builds** — Skips unchanged files and dependencies using mtime-based caching
- **Interactive setup** — `stoke init` guides you through project setup

## Installation

```bash
pip install stoke-build
```

Requires Python 3.11 or higher.

## Quick Start

```bash
# 1. Create a new project directory
mkdir myapp
cd myapp

# 2. Initialize with interactive setup
stoke init

# 3. Add your source files under src/

# 4. Build
stoke build
```

## Commands

| Command | Description |
| --- | --- |
| `stoke init` | Interactive project setup, generates `stoke.toml` |
| `stoke build [target]` | Build a target (or the default target if not specified) |
| `stoke build --force` | Ignore cache and rebuild everything |
| `stoke watch [target]` | Watch for file changes and rebuild automatically |
| `stoke hot-reload [target]` | Watch, rebuild, and restart the running process on changes |
| `stoke clean [target]` | Delete build artifacts (venv, cache, `__pycache__`) |
| `stoke clean --all` | Delete everything including the lock file |
| `stoke python list` | List all Python versions detected on the system |

## Configuration

`stoke.toml` example:

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"  # or "local"

[targets.myapp]
language = "python"
python_version = "3.12"       # optional, uses shell default if omitted
sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.myapp.deps]
requests = "2.31.0"
fastapi = ">=0.100.0"
```

### Lock file modes

- **`commit`** — Lock file is `stoke.lock` at the project root, committed to git for team reproducibility
- **`local`** — Lock file is `.stoke/lock.toml`, gitignored, per-developer

### Dependency version syntax

Follows pip specifier syntax:

- `"2.31.0"` — Exact version (equivalent to `==2.31.0`)
- `">=2.0.0"`, `"<3.0.0"`, `">=2.0,<3.0"` — Version ranges
- `"*"` or `""` — Any version

## How it works

On `stoke build`, stoke:

1. Reads `stoke.toml` and finds the target
2. Resolves the Python version:
   - If `stoke.lock` exists, uses the exact version pinned there
   - Otherwise, uses `python_version` from `stoke.toml`, or shell default
3. Creates a virtual environment at `.stoke/venv/[target]/` if needed
4. Installs dependencies:
   - From lock file if available (exact versions)
   - From `stoke.toml` if no lock exists (then writes lock)
   - Skipped if already up to date
5. Checks syntax of source files with `py_compile`, skipping unchanged files (mtime cache)
6. Saves cache to `.stoke/cache.json`

## Roadmap

- **v0.1** — Python build (venv, deps, syntax check, incremental builds)
- **v0.2** (current) — Watch mode (`stoke watch`), hot-reload (`stoke hot-reload`)
- **v0.3** — Java support
- **v0.4** — C/C++ support with `.so` reload and process restart modes
- **v0.5** — Package registry and `stoke install`, `stoke publish`

## Contributing

Bug reports and pull requests are welcome. Please open an issue first for major changes.

## License

MIT