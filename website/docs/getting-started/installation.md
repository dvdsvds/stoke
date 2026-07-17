# Installation

stoke is available for Windows, Linux, and macOS. Choose your platform:

## Windows

### Option 1: Windows installer (recommended)

Download the latest installer from [GitHub Releases](https://github.com/dvdsvds/stoke/releases/latest):

- File: `stoke-setup-X.Y.Z.exe`
- Install location: `%LOCALAPPDATA%\Programs\stoke`
- No admin privileges required
- Option to add to PATH during installation

After installation, verify:

```bash
stoke --version
```

### Option 2: pip

If you already have Python 3.10+ installed:

```bash
pip install stoke-build
```

## Linux / macOS

Install via pip:

```bash
pip install stoke-build
```

Requires Python 3.10 or higher.

## Verify installation

```bash
stoke --version
```

Should output the installed version.

## Requirements

stoke itself needs Python 3.10+, but it also uses language-specific tools depending on your project:

- **Python projects**: Python 3.8+ (any version stoke can detect)
- **Java projects**: JDK 17 or higher (Adoptium/OpenJDK/Zulu recommended)
- **C/C++ projects**: gcc, g++, or clang
- **C/C++ libraries**: vcpkg (auto-installable via `stoke install vcpkg`)

## Checking installed toolchains

After installation, check what languages stoke can build:

```bash
stoke python list      # Show detected Python installations
stoke java list        # Show detected JDKs
stoke c list           # Show detected C compilers
stoke cpp list         # Show detected C++ compilers
```

## Next steps

- [Quick Start](quick-start.md) — build your first project
- [Configuration](../configuration/stoke-toml.md) — `stoke.toml` reference