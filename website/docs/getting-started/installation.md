# Installation

stoke is available for Windows, Linux, and macOS. Choose your platform:

## Windows

### Option 1: Windows installer (recommended)

Download the latest installer from [GitHub Releases](https://github.com/dvdsvds/stoke/releases/latest):

- File: `stoke-setup-X.Y.Z.exe`
- Install location: `%LOCALAPPDATA%\Programs\stoke`
- **No prerequisites** — Python is bundled with the installer
- No admin privileges required
- Option to add to PATH during installation

After installation, verify:

```bash
stoke --version
```

## Linux / macOS

Download the tarball for your platform from [GitHub Releases](https://github.com/dvdsvds/stoke/releases/latest):

- File: `stoke-X.Y.Z-macos-<arch>.tar.gz` or `stoke-X.Y.Z-linux-<arch>.tar.gz`
- **No prerequisites** — Python is bundled with the binary

Extract it and add it to your `PATH`:

```bash
tar xzf stoke-*.tar.gz
export PATH="$PWD/stoke:$PATH"   # add to your shell profile to persist
```

Not code-signed: on macOS, Gatekeeper blocks the first run. Right-click (or Ctrl-click) the `stoke` binary, choose "Open", and confirm once — only needed the first time.

## Verify installation

```bash
stoke --version
```

Should output the installed version.

## Requirements

**stoke itself**: no prerequisites — Python is bundled in every installer/tarball.

**Language toolchains** (auto-installable via `stoke install --language=X`):
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