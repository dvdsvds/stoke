# stoke

A multi-language build tool with automatic dependency management and reproducible builds

Supports Python, Java, C, and C++

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

## Features

- **Python** — venv, pip dependencies, syntax check
- **Java** — JDK detection, Maven Central, IDE integration
- **C/C++** — gcc/g++, vcpkg integration, incremental builds
- Watch mode and hot-reload for all languages
- Reproducible builds via lock files
- Auto IDE integration (VSCode, IntelliJ, Eclipse)

## Documentation

Full documentation: [https://dvdsvds.github.io/stoke/](https://dvdsvds.github.io/stoke/)

Also available in the repo:
- [English README](./docs/README_en.md)
- [한국어 README](./docs/README_ko.md)

## Licenas

MIT