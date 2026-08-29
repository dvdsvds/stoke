# Commands Overview

stoke commands are organized by purpose.

## Build & run

| Command | Description |
|---------|-------------|
| [`stoke build`](build.md) | Compile the target |
| [`stoke run`](run.md) | Run the built target |
| [`stoke watch`](watch.md) | Auto-rebuild on file changes |
| [`stoke hot-reload`](hot-reload.md) | Rebuild + restart process |

## Project management

| Command | Description |
|---------|-------------|
| [`stoke init`](init.md) | Create a new project |
| [`stoke clean`](clean.md) | Delete build artifacts |
| [`stoke ide-sync`](ide-sync.md) | Generate IDE configs |

## Toolchain

| Command | Description |
|---------|-------------|
| `stoke python list` | List detected Python installations |
| `stoke java list` | List detected JDKs |
| `stoke c list` | List detected C compilers |
| `stoke cpp list` | List detected C++ compilers |

## C/C++ libraries

| Command | Description |
|---------|-------------|
| `stoke install vcpkg` | Install vcpkg |
| `stoke uninstall vcpkg` | Uninstall vcpkg |
| `stoke vcpkg install <lib>` | Install a library |
| `stoke vcpkg remove <lib>` | Remove a library |
| `stoke vcpkg list` | List installed libraries |
| `stoke vcpkg version` | Show vcpkg version |

See [vcpkg guide](../advanced/vcpkg.md) for details.

## Global options

Available across most commands:

### `--verbose` (`-v`)

Show detailed output:

```bash
stoke build --verbose
```

Default output is concise. Verbose shows compiler paths, dependency scanning, and per-file progress.

### Language selection

Set `STOKE_LANG=ko` in your environment to see help messages in Korean:

```bash
STOKE_LANG=ko stoke --help
```

Default is English. CLI output (build progress, errors) remains in English.

## Getting help

Each command has its own help:

```bash
stoke --help
stoke build --help
stoke vcpkg install --help
```