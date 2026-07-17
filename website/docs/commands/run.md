# stoke run

Run the built target.

## Usage

```bash
stoke run [target] [options]
```

If `target` is omitted, the first target in `stoke.toml` is used.

`stoke run` does **not** rebuild. It runs the previously built artifact. Run `stoke build` first if you've made changes.

## Options

| Option | Description |
|--------|-------------|
| `--debug` | Run the debug build (default) |
| `--release` | Run the release build |
| `--profile <name>` | Run a specific custom profile build |

## Examples

### Basic run

```bash
stoke run
```

Runs the default target with the debug profile.

### Specify target

```bash
stoke run myapp
```

### Run release build

```bash
stoke build --release
stoke run --release
```

### Run custom profile

```bash
stoke build --profile=small
stoke run --profile=small
```

## Language-specific behavior

### Python

Runs the `entry` script with the project's venv:

```toml
[targets.myapp]
language = "python"
entry = "src/main.py"
```
$ stoke run
Running: C:\myproject\src\main.py
Hello from stoke!

### Java

Runs the class specified by `main_class`:

```toml
[targets.myapp]
language = "java"
main_class = "com.example.Main"
```
$ stoke run
Running: com.example.Main
Hello from stoke!

The classpath includes compiled `.class` files and Maven dependencies.

### C / C++

Runs the compiled executable:
$ stoke run
Running: .stoke\cpp\myapp\debug\myapp.exe
Hello from stoke!

## Exit codes

The exit code of `stoke run` matches the target's exit code. If your program returns non-zero, `stoke run` also returns non-zero.

## Related

- [`stoke build`](build.md) — build before running
- [`stoke hot-reload`](hot-reload.md) — rebuild and restart on file changes