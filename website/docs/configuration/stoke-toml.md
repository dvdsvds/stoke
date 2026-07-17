# stoke.toml Reference

Complete reference for the `stoke.toml` configuration file.

## File structure

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]

[targets.myapp.deps]
fmt = "*"

[profiles.custom]
compile_flags = ["-O2"]
```

Sections:

- **`[project]`** — project-wide metadata
- **`[targets.<name>]`** — one section per build target
- **`[targets.<name>.deps]`** — dependencies for a target
- **`[profiles.<name>]`** — build profiles (C/C++ only)

## `[project]`

Project-level configuration.

```toml
[project]
name = "myapp"           # Required. Project name.
version = "0.1.0"        # Optional. Project version.
lock_mode = "auto"       # Optional. Lock file behavior.
jobs = 4                 # Optional. Default parallel build workers.
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Project name |
| `version` | string | Semver-ish version |
| `lock_mode` | `"auto"` \| `"strict"` \| `"off"` | Lock file behavior (default: `"auto"`) |
| `jobs` | int | Default parallel workers for build (C/C++) |

### `lock_mode` values

- **`"auto"`**: use lock file if present, update as needed
- **`"strict"`**: require lock file, fail if versions don't match
- **`"off"`**: don't use or write lock file

## `[targets.<name>]`

One section per build target. Multiple targets allowed:

```toml
[targets.server]
language = "python"
entry = "src/server.py"

[targets.worker]
language = "python"
entry = "src/worker.py"
```

Build a specific target:

```bash
stoke build server
stoke run worker
```

If no target is specified, the first one in the file is used.

### Common fields

| Field | Required | Description |
|-------|----------|-------------|
| `language` | Yes | `"python"`, `"java"`, `"c"`, `"cpp"` |
| `sources` | Depends | Glob patterns for source files |

### Python-specific fields

| Field | Description |
|-------|-------------|
| `python_version` | Required Python version |
| `entry` | Entry script path |

### Java-specific fields

| Field | Description |
|-------|-------------|
| `java_version` | Required JDK major version |
| `main_class` | Fully qualified main class |

### C/C++-specific fields

| Field | Description |
|-------|-------------|
| `c_standard` | C standard (`"c11"`, `"c17"`, etc.) |
| `cpp_standard` | C++ standard (`"c++17"`, `"c++20"`, etc.) |
| `include_dirs` | Extra include directories |
| `jobs` | Override project-level `jobs` |

## `[targets.<name>.deps]`

Dependencies for a specific target. Format varies by language.

### Python (pip)

```toml
[targets.myapp.deps]
requests = "*"
flask = ">=2.0"
numpy = "==1.24.3"
mypackage = "git+https://github.com/user/repo"
```

### Java (Maven)

```toml
[targets.myapp.deps]
"com.google.code.gson:gson" = "2.10.1"
"org.slf4j:slf4j-api" = "2.0.9"
```

Key format: `"groupId:artifactId"`.

### C / C++ (vcpkg)

```toml
[targets.myapp.deps]
fmt = "*"
sqlite3 = "*"
```

Version is passed to vcpkg. `"*"` means latest available.

## `[profiles.<name>]`

Build profiles for C/C++.

```toml
[profiles.small]
compile_flags = ["-Os", "-flto"]
defines = { NDEBUG = 1 }

[profiles.clang]
compiler = "clang"
```

See [Profiles](profiles.md) for the full reference.

## Full example

Multi-target project:

```toml
[project]
name = "myservice"
version = "1.0.0"

# Python backend
[targets.backend]
language = "python"
python_version = "3.12"
entry = "backend/main.py"
sources = ["backend/**/*.py"]

[targets.backend.deps]
fastapi = "*"
uvicorn = "*"

# C++ engine
[targets.engine]
language = "cpp"
sources = ["engine/src/**/*.cpp"]
cpp_standard = "c++20"
include_dirs = ["engine/include"]
jobs = 8

[targets.engine.deps]
fmt = "*"
spdlog = "*"

# Custom profile
[profiles.native]
compile_flags = ["-O3", "-march=native"]
```

Build individual targets:

```bash
stoke build backend
stoke build engine --profile=native
```

## Related

- [Profiles](profiles.md)
- [Lock file](lock-file.md)
- Language guides: [Python](../languages/python.md), [Java](../languages/java.md), [C/C++](../languages/cpp.md)