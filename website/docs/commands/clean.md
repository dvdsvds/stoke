# stoke clean

Delete build artifacts.

## Usage

```bash
stoke clean [target] [options]
```

If `target` is omitted, all targets are cleaned.

## Options

| Option | Description |
|--------|-------------|
| `--all` | Also delete the lock file (full reset) |

## Examples

### Clean all targets

```bash
stoke clean
```

Removes:

- `.stoke/{language}/{target}/` for each target
- `.stoke/cache.json`
- All `__pycache__` folders in the project

### Clean a specific target

```bash
stoke clean myapp
```

Only removes artifacts for `myapp`.

### Full reset

```bash
stoke clean --all
```

Also deletes `.stoke/lock.toml`, forcing dependency re-resolution on the next build.

Use this if:
- Lock file is corrupted
- You want to pull the latest versions of dependencies
- Switching Python/JDK versions caused issues

## What gets deleted

| Item | `clean` | `clean --all` |
|------|---------|---------------|
| Object files (`.o`, `.class`) | ✓ | ✓ |
| Executables | ✓ | ✓ |
| Python venv | ✓ | ✓ |
| `.stoke/cache.json` | ✓ | ✓ |
| `__pycache__/` | ✓ | ✓ |
| `.stoke/lock.toml` | | ✓ |
| IDE files (`.vscode/`, `.classpath`, etc.) | | |

IDE files are never deleted; they're regenerated on the next build.

## After clean

Next build will:

- Recompile everything (no cache)
- Recreate the Python venv (if applicable)
- Reinstall dependencies (with `--all`)

## Related

- [`stoke build --force`](build.md) — force rebuild without deleting artifacts