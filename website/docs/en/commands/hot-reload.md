# stoke hot-reload

Watch for file changes, rebuild, and restart the running process.

## Usage

```bash
stoke hot-reload [target] [options]
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
stoke hot-reload
```

Output:
==================================================
[hot-reload] Rebuilding 'myapp'...
Using c compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp
[hot-reload] Starting: .stoke\cpp\myapp\debug\myapp.exe
[hot-reload] Watching: C:\myproject\src
[hot-reload] Press Ctrl+C to stop.
Hello from stoke!

When you save a file, stoke stops the process, rebuilds, and restarts:
[hot-reload] Detected changes in: src\main.c
[hot-reload] Stopping process...
==================================================
[hot-reload] Rebuilding 'myapp'...
Using c compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp
[hot-reload] Starting: .stoke\cpp\myapp\debug\myapp.exe
Hello from stoke!

Press Ctrl+C to stop the watcher and the process.

## When to use it

Best for long-running processes:

- Web servers (Flask, Spring Boot, etc.)
- Development scripts with state
- Background workers

For batch programs that finish and exit quickly, `stoke watch` is usually enough.

## Language-specific behavior

Same as [`stoke run`](run.md):

- **Python**: runs the `entry` script
- **Java**: runs `main_class`
- **C/C++**: runs the compiled executable

## C/C++ note

For C/C++, stoke stops the process **before** rebuilding. This is necessary because the linker can't overwrite a running executable on most platforms.

For Python and Java, stoke rebuilds first and stops the process after, since there's no such limitation.

## Related

- [`stoke watch`](watch.md) — rebuild only, don't restart
- [`stoke run`](run.md) — single run