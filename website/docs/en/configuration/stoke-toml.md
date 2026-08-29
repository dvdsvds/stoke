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
| `pre_build` | No | Shell commands to run before the build, in order |
| `post_build` | No | Shell commands to run after the build, in order |
| `depends_on` | No | List of target names this target depends on; built first, in order |
| `build_system` | No | C/C++ only. Set to `"cmake"` to delegate to CMake instead of stoke's own build model |
| `source_dir` | No | C/C++ + `build_system = "cmake"` only. Folder containing `CMakeLists.txt`, relative to the project root (default `"."`) |

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

## Build hooks

```toml
[targets.myapp]
language = "python"
pre_build = ["echo starting build"]
post_build = ["cp dist/myapp ./release/myapp"]
```

Runs through the shell, in declared order, for `stoke build`, `stoke build --all`, `stoke watch`, and `stoke hot-reload` alike. A non-zero `pre_build` command skips the build entirely; a failing `post_build` command fails the build.

> **Security note**: these commands are whatever string is in `stoke.toml`, executed verbatim through the shell with your user's permissions. Don't run `stoke build` on a `stoke.toml` you haven't read from a repository you don't trust.

## Target dependencies

```toml
[targets.backend]
language = "python"
depends_on = ["shared_lib"]
```

`stoke build backend` builds `shared_lib` first automatically. `stoke build --all` builds targets with no unmet dependencies in parallel, waits for a target's `depends_on` to finish before starting it, and skips (rather than attempts) a target whose dependency failed. Unknown target references and dependency cycles are rejected when `stoke.toml` loads, before any build starts.

## CMake for C/C++

For a C/C++ target that already has its own `CMakeLists.txt`, delegate to CMake instead of stoke's own compile model:

```toml
[targets.engine]
language = "cpp"
build_system = "cmake"
source_dir = "."   # folder with CMakeLists.txt, relative to the project root
```

`stoke build`/`run`/`watch`/`hot-reload`/`clean` all work the same way as with stoke's own C/C++ model, but internally run `cmake -S <source_dir> -B <build_dir>` then `cmake --build <build_dir>`, and locate the produced executable automatically. `c_standard`/`cpp_standard`, `[profiles.*].compile_flags`/`defines`/`compiler`, and `includes` are ignored on this path — `CMakeLists.txt` owns those; only the profile name maps to `CMAKE_BUILD_TYPE` (`debug` → `Debug`, `release` → `Release`).

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
- Language guides: [Python](../languages/python.md), [Java](../languages/java.md), [C/C++](../languages/cpp.md), [Go](../languages/go.md), [Rust](../languages/rust.md), [Kotlin](../languages/kotlin.md), [C#](../languages/csharp.md), [Ruby](../languages/ruby.md), [PHP](../languages/php.md), [JavaScript](../languages/javascript.md), [TypeScript](../languages/typescript.md)