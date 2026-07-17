# stoke build

Build a target.

## Usage

```bash
stoke build [target] [options]
```

If `target` is omitted, the first target in `stoke.toml` is used.

## Options

| Option | Description |
|--------|-------------|
| `--force` | Ignore cache and rebuild everything |
| `--debug` | Build with the debug profile (default) |
| `--release` | Build with the release profile |
| `--profile <name>` | Build with a custom profile from `stoke.toml` |
| `-v`, `--verbose` | Show detailed build output |

## Examples

### Basic build

```bash
stoke build
```

Builds the default target with the debug profile.

### Specify target

```bash
stoke build myapp
```

Builds the `myapp` target.

### Release build

```bash
stoke build --release
```

Optimized build (`-O2` for C/C++, defines `NDEBUG`).

### Custom profile

```toml
# stoke.toml
[profiles.small]
compile_flags = ["-Os", "-flto"]
defines = { NDEBUG = 1 }
```

```bash
stoke build --profile=small
```

### Force rebuild

```bash
stoke build --force
```

Ignores the cache and recompiles everything. Useful when you suspect stale artifacts.

### Verbose output

```bash
stoke build -v
```

Shows compiler paths, per-file compilation status, and detailed steps.

## Output structure

Build artifacts are organized by language, target, and profile:
.stoke/
├── {language}/
│   └── {target}/
│       └── {profile}/
│           ├── objects/         # C/C++ .o files
│           ├── classes/         # Java .class files
│           └── {target}.exe     # Final executable
├── cache.json                   # Incremental build cache
└── lock.toml                    # Locked versions

Example for a C project:
.stoke/
├── c/
│   └── myapp/
│       ├── debug/
│       │   ├── objects/
│       │   └── myapp.exe
│       └── release/
│           ├── objects/
│           └── myapp.exe
├── cache.json
└── lock.toml

## Incremental compilation

stoke tracks file modifications and header dependencies. Only changed files are recompiled.

For C/C++, header dependencies are tracked via gcc's `-MMD` flag. If `header.h` changes, all files that `#include "header.h"` (directly or indirectly) will be recompiled.

To bypass the cache, use `--force`.

## Build profiles

Default profiles:

- **debug** — `-O0 -g -Wall`, defines `DEBUG` (C/C++ only)
- **release** — `-O2`, defines `NDEBUG` (C/C++ only)

Note: profiles only affect C/C++ builds. Python and Java ignore profiles.

Custom profiles are defined in `stoke.toml`:

```toml
[profiles.myprofile]
compile_flags = ["-O3", "-march=native"]
defines = { MYFLAG = 1 }
compiler = "clang"  # optional: override compiler
```

See [Profiles](../configuration/profiles.md) for details.

## Related

- [`stoke run`](run.md) — run the built target
- [`stoke watch`](watch.md) — auto-rebuild on changes
- [`stoke clean`](clean.md) — remove build artifacts
- [Profiles](../configuration/profiles.md) — profile system reference