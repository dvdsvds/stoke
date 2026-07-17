# C / C++

stoke handles C and C++ projects with header dependency tracking, parallel compilation, build profiles, and vcpkg integration.

## Example `stoke.toml`

C++ project:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]
cpp_standard = "c++20"
```

C project:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "c"
sources = ["src/**/*.c"]
c_standard = "c11"

[targets.myapp.deps]
sqlite3 = "*"
```

## Target fields

| Field | Required | Description |
|-------|----------|-------------|
| `language` | Yes | `"c"` or `"cpp"` |
| `sources` | Yes | Glob patterns for `.c`/`.cpp` files |
| `c_standard` | No | e.g. `"c11"`, `"c17"` (C only) |
| `cpp_standard` | No | e.g. `"c++17"`, `"c++20"`, `"c++23"` (C++ only) |
| `deps` | No | vcpkg libraries |
| `jobs` | No | Parallel compilation workers (default: CPU count) |

## Compiler detection

stoke uses:

- **Linux**: `gcc` / `g++` (default)
- **macOS**: `clang` / `clang++` (default)
- **Windows**: `gcc` / `g++` from MSYS2/MinGW (default)

Override with a build profile:

```toml
[profiles.clang]
compiler = "clang"
```

```bash
stoke build --profile=clang
```

Check detected compilers:

```bash
stoke c list       # C compilers
stoke cpp list     # C++ compilers
```

## Header dependencies

stoke uses gcc's `-MMD` flag to track which headers each source includes. If a header changes, all files that include it are recompiled.

Example: change `include/utils.h` → all `.cpp` files that `#include "utils.h"` (directly or transitively) rebuild.

Header dependency files (`.d`) are stored alongside object files in `.stoke/`.

## Include paths

stoke automatically adds:

- `src/` (project root sources)
- `include/` (if it exists)
- vcpkg include paths (for installed dependencies)
- User-specified paths via `include_dirs`

You can add extra paths:

```toml
[targets.myapp]
include_dirs = ["third_party/include"]
```

## Include convention

Use explicit paths in `#include`:

```cpp
#include "hardware/cpu.hpp"        // ✓ good
#include "cpu.hpp"                 // ✗ ambiguous
```

Same convention as Python/Java/Rust/Go. Makes imports unambiguous and refactoring safer.

## Parallel compilation

stoke compiles files in parallel by default (worker count = CPU cores).

Override:

```toml
[targets.myapp]
jobs = 4
```

Or override globally in `[project]`.

## Build profiles

Default profiles:

- **debug** — `-O0 -g -Wall`, defines `DEBUG`
- **release** — `-O2`, defines `NDEBUG`

Custom profiles in `stoke.toml`:

```toml
[profiles.small]
compile_flags = ["-Os", "-flto"]
defines = { NDEBUG = 1 }

[profiles.native]
compile_flags = ["-O3", "-march=native"]

[profiles.clang]
compiler = "clang"
compile_flags = ["-O2"]
```

Build with:

```bash
stoke build --profile=small
```

See [Profiles](../configuration/profiles.md) for details.

## Dependencies (vcpkg)

C/C++ libraries via [vcpkg](https://vcpkg.io):

```toml
[targets.myapp.deps]
sqlite3 = "*"
fmt = "*"
```

First install vcpkg:

```bash
stoke install vcpkg
```

Then install libraries:

```bash
stoke vcpkg install sqlite3
stoke vcpkg install fmt
```

Or add them manually to `stoke.toml` and run `stoke build` — stoke will install them.

See [vcpkg guide](../advanced/vcpkg.md).

## IDE integration

`stoke build` generates:

- `compile_commands.json` — for clangd, VSCode C/C++ extension, etc.
- `.vscode/c_cpp_properties.json` — for Microsoft C/C++ extension
- `.vscode/settings.json` — file exclusions, extension settings

Open the project in VSCode with the C/C++ extension — IntelliSense works immediately.

## Output structure
.stoke/
├── cpp/
│   └── myapp/
│       ├── debug/
│       │   ├── objects/       # .o files
│       │   ├── myapp.d.*      # header dep files
│       │   └── myapp.exe
│       └── release/
│           ├── objects/
│           └── myapp.exe

## Related

- [`stoke build`](../commands/build.md)
- [Profiles](../configuration/profiles.md)
- [vcpkg](../advanced/vcpkg.md)