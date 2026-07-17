# stoke watch

Watch for file changes and rebuild automatically.

## Usage

```bash
stoke watch [target] [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--debug` | Debug build (default) |
| `--release` | Release build |
| `--profile <name>` | Custom profile |
| `-v`, `--verbose` | Show detailed build output |

## Example

```bash
stoke watch
```

Output:
==================================================
[watch] Rebuilding 'myapp'...
Using c compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp
[watch] Watching: C:\myproject\src
[watch] Press Ctrl+C to stop.

When you save a file, stoke automatically rebuilds:
[watch] Detected changes in: src\main.c
==================================================
[watch] Rebuilding 'myapp'...
Using c compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp

Press Ctrl+C to stop.

## What's watched

stoke watches the directories that contain your `sources` patterns. For example, with:

```toml
[targets.myapp]
sources = ["src/**/*.c"]
```

stoke watches `src/`.

Only files matching the source extensions for your language are considered:

- **Python**: `.py`
- **Java**: `.java`
- **C**: `.c`, `.h`
- **C++**: `.cpp`, `.hpp`, `.h`

Other file changes are ignored.

## Debouncing

Multiple rapid changes are debounced. If you save 5 files in quick succession, stoke rebuilds once, not 5 times.

## Profiles work with watch

Watch respects the profile you choose:

```bash
stoke watch --release
```

Builds into `.stoke/{lang}/{target}/release/` on every change.

## Related

- [`stoke hot-reload`](hot-reload.md) — watch + restart the process
- [`stoke build`](build.md) — single build