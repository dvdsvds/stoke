# Troubleshooting

Common issues and solutions.

## Build errors

### `stoke.toml not found`

**Cause**: You ran stoke from outside a project directory.

**Fix**: `cd` into the project root (the directory containing `stoke.toml`).

### `target 'X' not found in stoke.toml`

**Cause**: The specified target doesn't exist.

**Fix**: List valid targets by opening `stoke.toml`. Available targets are shown in the error output.

### `profile 'X' not found`

**Cause**: Custom profile doesn't exist in `stoke.toml`.

**Fix**: Check `[profiles.*]` sections in `stoke.toml`. Only `debug`, `release`, and custom profiles you define are valid.

### `Python X.Y not found`

**Cause**: No Python matching `python_version` is installed.

**Fix**: 

1. Check detected Pythons: `stoke python list`
2. Install the required Python version, or
3. Change `python_version` in `stoke.toml` to a version you have

### `JDK X not found`

**Cause**: No JDK with the required major version.

**Fix**:

1. Check detected JDKs: `stoke java list`
2. Install a matching JDK (Adoptium recommended: [adoptium.net](https://adoptium.net))
3. Set `JAVA_HOME` if needed
4. Or change `java_version` in `stoke.toml`

### `No C compiler detected`

**Cause**: gcc/clang not in `PATH`.

**Fix**:

- **Windows**: Install MSYS2 and run `pacman -S mingw-w64-ucrt-x86_64-gcc`. Add MSYS2 bin to `PATH`.
- **macOS**: Install Xcode Command Line Tools: `xcode-select --install`
- **Linux**: `sudo apt install build-essential` (Ubuntu/Debian) or equivalent

## Runtime errors

### `stoke run` fails silently

**Cause**: The target hasn't been built yet.

**Fix**: `stoke build` first.

### Python: `ModuleNotFoundError`

**Cause**: Import paths not set up correctly.

**Fix**:

- Ensure each folder has an `__init__.py`
- Use full paths from `src/`: `from utils.helpers import ...`
- Check [Python source layout](languages/python.md#source-layout)

### Java: `Could not find or load main class`

**Cause**: `main_class` in `stoke.toml` doesn't match the actual class name.

**Fix**: Verify the fully qualified class name matches. Example:

```java
// src/main/java/com/example/Main.java
package com.example;
public class Main { ... }
```

```toml
main_class = "com.example.Main"    # fully qualified
```

## Cache / Lock issues

### Stale builds after external changes

**Cause**: You changed something outside `sources` (e.g. moved files, changed env vars) and cache is stale.

**Fix**: Force rebuild:

```bash
stoke build --force
```

### Lock file mismatch

**Cause**: Lock file references tools/deps that no longer exist.

**Fix**: Full reset:

```bash
stoke clean --all
stoke build
```

## vcpkg issues

### Library install takes forever

**Cause**: vcpkg builds from source. Some libraries (Boost, Qt) take a very long time.

**Fix**: Be patient. First install is slow; subsequent uses are fast.

### `Library not found` after install

**Cause**: vcpkg installed the library but stoke's cache is stale.

**Fix**:

```bash
stoke build --force
```

### vcpkg corrupted

**Cause**: Interrupted install or system issue.

**Fix**:

```bash
stoke uninstall vcpkg
stoke install vcpkg
stoke build --force
```

## IDE issues

### VSCode showing wrong Python interpreter

**Cause**: VSCode Python extension picked a global Python instead of the venv.

**Fix**:

1. `stoke build` to regenerate `.vscode/settings.json`
2. Ctrl+Shift+P → "Python: Select Interpreter" → pick `.stoke/python/<target>/venv/`

### VSCode lag on some systems

**Cause**: File watcher or extensions overloading.

**Fix**:

1. Confirm `.vscode/settings.json` excludes `.stoke/`
2. Disable hardware acceleration: settings.json → `"disable-hardware-acceleration": true`
3. Disable unused extensions
4. Restart VSCode

Tracking issue: [VSCode lag on some systems](https://github.com/dvdsvds/stoke/issues)

### C++ IntelliSense not working

**Cause**: `compile_commands.json` missing or IDE not picking it up.

**Fix**:

1. Run `stoke build` to generate `compile_commands.json`
2. Ensure your extension reads it (Microsoft C/C++ extension reads `.vscode/c_cpp_properties.json`; clangd reads `compile_commands.json`)

## watch / hot-reload issues

### Changes not detected

**Cause**: Files are outside the `sources` glob patterns.

**Fix**: Check `sources` in `stoke.toml` covers all your source files.

### hot-reload doesn't restart

**Cause**: Process didn't exit cleanly, or output buffered.

**Fix**:

- Try again (transient issues)
- For Python/Java, ensure your program handles SIGTERM/SIGINT properly

## Still stuck?

- Search or open an issue: [github.com/dvdsvds/stoke/issues](https://github.com/dvdsvds/stoke/issues)
- Check the [FAQ](faq.md)