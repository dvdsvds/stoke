# vcpkg Integration

stoke integrates with [vcpkg](https://vcpkg.io) for C/C++ dependency management.

## Installation

Install vcpkg:

```bash
stoke install vcpkg
```

This clones vcpkg into a stoke-managed location and bootstraps it. No admin privileges needed.

Check installation:

```bash
stoke vcpkg version
```

Uninstall:

```bash
stoke uninstall vcpkg
```

## Installing libraries

Two ways:

### Method 1: Direct install command

```bash
stoke vcpkg install fmt
stoke vcpkg install sqlite3
```

This:

1. Downloads and builds the library via vcpkg
2. Adds it to `stoke.toml` under `[targets.<name>.deps]`

By default, the library is added to the first target. Specify a target:

```bash
stoke vcpkg install fmt --target=engine
```

### Method 2: Add to stoke.toml manually

```toml
[targets.myapp.deps]
fmt = "*"
sqlite3 = "*"
```

Then run:

```bash
stoke build
```

stoke automatically installs any declared but missing libraries.

## Removing libraries

```bash
stoke vcpkg remove fmt
```

This:

1. Removes from `stoke.toml`
2. Runs vcpkg's remove command

## Listing installed libraries

```bash
stoke vcpkg list
```

Or for a specific target:

```bash
stoke vcpkg list --target=engine
```

## Specific versions

Install a specific version:

```bash
stoke vcpkg install fmt --version=10.1.1
```

Or in `stoke.toml`:

```toml
[targets.myapp.deps]
fmt = "10.1.1"
```

Use `"*"` for the latest available:

```toml
[targets.myapp.deps]
fmt = "*"
```

## How stoke uses vcpkg

At build time:

1. stoke reads `[targets.<name>.deps]`
2. Verifies each library is installed via vcpkg
3. Adds vcpkg include paths (e.g. `installed/x64-mingw-dynamic/include/`) to compile flags
4. Links vcpkg library files (`.a`, `.lib`, `.so`, etc.) at link time

Include paths and library paths are automatic. In your code:

```cpp
#include <fmt/format.h>          // works, no extra config needed
```

## Language compatibility

Some libraries are C-only, some are C++-only.

C project:

```toml
[targets.myapp]
language = "c"

[targets.myapp.deps]
sqlite3 = "*"    # ✓ C library
fmt = "*"        # ✗ C++ only, stoke will error
```

C++ project:

```toml
[targets.myapp]
language = "cpp"

[targets.myapp.deps]
sqlite3 = "*"    # ✓ works (C libraries usable from C++)
fmt = "*"        # ✓ C++ library
```

stoke validates compatibility before installing.

## Triplets

vcpkg builds libraries per **triplet** (architecture + platform + linkage).

Auto-detected default:

- Windows MinGW64: `x64-mingw-dynamic`
- Windows MSVC: `x64-windows`
- Linux x64: `x64-linux`
- macOS: `x64-osx` or `arm64-osx`

Stored in `.stoke/lock.toml` per dependency.

## Troubleshooting

### Library not found after install

Try `stoke build --force` to clear the cache and re-scan vcpkg.

### Long install times

First install of some libraries (like Boost, Qt) can take an hour. This is vcpkg building from source. Subsequent builds are fast.

### Reset vcpkg

If vcpkg gets corrupted:

```bash
stoke uninstall vcpkg
stoke install vcpkg
stoke build --force
```

## Related

- [`stoke.toml` reference](../configuration/stoke-toml.md)
- [Languages / C/C++](../languages/cpp.md)