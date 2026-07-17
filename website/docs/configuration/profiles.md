# Build Profiles

Build profiles let you switch between different build configurations without editing your code. Currently supported for **C and C++** only.

## Built-in profiles

stoke provides two default profiles:

### debug

```toml
compile_flags = ["-O0", "-g", "-Wall"]
defines = { DEBUG = 1 }
```

Default when you run `stoke build`. Good for development:

- No optimization (`-O0`)
- Full debug info (`-g`)
- All warnings enabled (`-Wall`)
- `DEBUG` defined for conditional compilation

### release

```toml
compile_flags = ["-O2"]
defines = { NDEBUG = 1 }
```

Use with `--release`:

- Optimization (`-O2`)
- `NDEBUG` defined (disables `assert()`, etc.)

## Using profiles

```bash
stoke build                     # debug (default)
stoke build --debug             # debug (explicit)
stoke build --release           # release
stoke build --profile=    # custom profile
```

Corresponding `stoke run` and `stoke watch`:

```bash
stoke run --release
stoke watch --profile=custom
stoke hot-reload --release
```

## Custom profiles

Define custom profiles in `stoke.toml`:

```toml
[profiles.<name>]
compile_flags = [...]     # extra compiler flags
defines = { KEY = value } # preprocessor defines
compiler = "..."          # optional: override compiler
```

### Example: size-optimized

```toml
[profiles.small]
compile_flags = ["-Os", "-flto", "-s"]
defines = { NDEBUG = 1 }
```

```bash
stoke build --profile=small
```

### Example: native optimization

```toml
[profiles.native]
compile_flags = ["-O3", "-march=native"]
defines = { NDEBUG = 1, NATIVE_BUILD = 1 }
```

### Example: clang override

```toml
[profiles.clang]
compiler = "clang"
compile_flags = ["-O2", "-Wall", "-Wextra"]
```

The `compiler` field overrides the default compiler for this profile. Value: `"gcc"` or `"clang"`.

## Output directories

Each profile builds into its own directory:
.stoke/
└── cpp/
└── myapp/
├── debug/
│   └── myapp.exe
├── release/
│   └── myapp.exe
└── small/
└── myapp.exe

Rebuilding a different profile doesn't affect others. You can maintain multiple builds simultaneously.

## Conflicts

You can't combine flag styles:

```bash
stoke build --debug --release           # error: can't combine
stoke build --release --profile=small   # error: can't combine
```

## Not available for Python/Java

Profiles apply to C/C++ only. Python and Java builds ignore the profile flag but still use profile-based output directories:
.stoke/
├── python/
│   └── myapp/
│       └── venv/            # same venv regardless of profile
└── java/
└── myapp/
└── debug/           # default profile dir
└── classes/

## Available flags

Profile fields:

| Field | Type | Description |
|-------|------|-------------|
| `compile_flags` | list[string] | Extra flags for the compiler |
| `defines` | table | Preprocessor `-D` defines |
| `compiler` | string | Override compiler (`"gcc"` or `"clang"`) |

## Related

- [`stoke build`](../commands/build.md)
- [Languages / C/C++](../languages/cpp.md)