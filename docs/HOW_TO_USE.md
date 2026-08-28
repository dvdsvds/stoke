# stoke — How To Use (v1.5.1)

A practical guide: how to actually use stoke day to day, what setups it's good for, and concrete commands for each scenario.

## TL;DR

```bash
mkdir myapp && cd myapp
stoke init      # pick a language, answer a few prompts
stoke build     # compile/prepare
stoke run       # run it
```

One `stoke.toml` per project. One CLI for build/run/watch/scaffold across 12 languages. `stoke.toml` is meant to be managed entirely through the CLI — you're not expected to hand-edit it (`stoke init`, run again inside an existing project, adds targets to it instead of asking you to edit TOML yourself).

---

## 1. Is stoke a good fit for what you're building?

**Good fit:**
- A small-to-medium project or a team of roughly 10–30 people.
- A single service, or a handful of related services/targets in one repo (a Python API + a Go worker + a small CLI tool, say) where you'd like one consistent `build`/`run`/`watch` command regardless of which target you're touching.
- Teams onboarding new members often and wanting a single `stoke init --language=... --yes` line to replace a wiki page of manual setup steps.
- Projects that want reproducible builds (a committed lock file) without adopting a heavier tool (Bazel, Nx, Turborepo) and its learning curve.
- Environments where you already use a specific toolchain per language (Cargo, Gradle, `dotnet`, Bundler, Composer, npm, Maven Central) — stoke delegates to them rather than reinventing dependency resolution, so you keep using `Cargo.toml`/`build.gradle.kts`/etc. as normal.

**Not a good fit (see §9 for the full list):**
- Large C/C++ codebases needing Meson or another generated build graph (CMake projects can opt into `build_system = "cmake"` instead — see §9 below).
- Windows-native C++ shops that need MSVC (stoke only drives gcc/clang).
- Teams that need a plugin system to add a company-internal language/framework without patching stoke's own source.

---

## 2. Install

**Windows** — native installer, bundles Python, no prerequisites:
Download from the [Releases page](https://github.com/dvdsvds/stoke/releases/latest).

**Linux/macOS** — native tarball, bundles Python, no prerequisites:
Download `stoke-X.Y.Z-<platform>-<arch>.tar.gz` from the [Releases page](https://github.com/dvdsvds/stoke/releases/latest), extract it, and add it to your `PATH`:
```bash
tar xzf stoke-*.tar.gz
export PATH="$PWD/stoke:$PATH"
```
Not code-signed: macOS Gatekeeper blocks the first run — right-click the `stoke` binary, choose "Open", confirm once.

---

## 3. Your first project

```bash
mkdir myapp && cd myapp
stoke init
```

You'll be walked through: project name → language → language-specific questions (Python version, Java version, C/C++ standard, optional toolchain pin, etc.) → lock mode (`commit` or `local`). This writes `stoke.toml` plus example source files.

```bash
stoke build      # compiles/prepares the target
stoke run        # runs it
stoke watch       # rebuilds automatically on file changes
```

**Skip the prompts** if you already know what you want, or you're scripting this (CI, onboarding):

```bash
stoke init --language=python --name=myapp --version=3.12 --lock-mode=commit --yes
```

**Scaffold a known framework directly** instead of a bare language:

```bash
stoke init fastapi        # or: flask, django, spring-boot, gin, echo, fiber, chi,
                           # actix-web, axum, rocket, ktor, spring-boot-kotlin,
                           # aspnet-core, sinatra, slim, express, fastify,
                           # nextjs, nestjs, vite, nuxt, sveltekit, hono
```

---

## 4. Growing into multiple targets

If `stoke.toml` already exists and you run `stoke init` again, it offers **"Add a new target to this project"** instead of forcing you to overwrite. This is the intended way to grow a project — never hand-edit `[targets.*]` blocks into `stoke.toml` yourself.

```
$ stoke init
stoke.toml already exists at ./stoke.toml

What would you like to do?
  1. Add a new target to this project (default)
  2. Overwrite (start over with a new stoke.toml)
Select [1-2, default 1]: 1

Target name: worker
Language:
  1. Python (default)  2. Java  3. C  4. C++  5. Go  6. Rust
  7. Kotlin  8. C#  9. Ruby  10. PHP  11. JavaScript  12. TypeScript
Select [1-12, default 1]: 5

Added target 'worker' (go) to ./stoke.toml
Source files created under: ./worker
```

The result is one `stoke.toml` with multiple `[targets.*]` blocks — e.g. a Python API and a Go worker side by side:

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.api]
language = "python"
sources = ["api/src/main.py"]
entry = "api/src/main.py"
python_version = "3.12"

[targets.worker]
language = "go"
```

Build/run either one independently, or all of them at once:

```bash
stoke build api
stoke build worker
stoke build --all      # builds every target in parallel
stoke run api
stoke run worker
```

**How each language keeps a second target independently buildable:**

| Language group | How isolation works |
| --- | --- |
| Python, Java, C, C++, Ruby, PHP, JavaScript, TypeScript | `target.sources`/`target.entry` in `stoke.toml` scope the build to specific files under `<target_name>/`. |
| Go | Each target is its own package under `<target_name>/`, sharing one root `go.mod` (Go's own `cmd/api/`, `cmd/worker/` convention). `stoke` builds `./<target_name>` instead of the whole module. |
| Rust | Each target after the first becomes a Cargo **workspace member** (`<target_name>/Cargo.toml`); the root stays a normal package. `stoke` passes `--manifest-path` explicitly. |
| Kotlin | Each target after the first becomes a Gradle **subproject** (`<target_name>/build.gradle.kts`, registered via `include()` in `settings.gradle.kts`). `stoke` always uses colon-qualified task paths (`:worker:build`) so building one target never triggers the others. |
| C# | Each target gets its own `.csproj` under `<target_name>/`. `stoke` passes that `.csproj` path explicitly to `dotnet build`, and patches the root `.csproj` to exclude the new target's folder from its own compile globbing (SDK-style `.csproj` recurses by default, which is what this exclusion works around). |

All four of the above (Go/Rust/Kotlin/C#) were fixed to support this in the same session that produced this doc — if you're on an older stoke build, a second Go/Rust/Kotlin/C# target may not build independently; upgrade first.

**Removing a target:** run `stoke init` again and pick **"Remove a target from this project"** instead. It undoes whatever the add-target flow registered for that target's language — a Rust workspace member, a Kotlin `settings.gradle.kts` `include()`, a C#'s root `.csproj` exclude rule — and then asks separately whether to also delete the target's `<target_name>/` source directory (default: no, so you don't lose files by accident).

```
$ stoke init
stoke.toml already exists at ./stoke.toml

What would you like to do?
  1. Add a new target to this project (default)
  2. Remove a target from this project
  3. Overwrite (start over with a new stoke.toml)
Select [1-3, default 1]: 2

Select a target to remove:
  1. api (default)
  2. worker
Select [1-2, default 1]: 2
Remove target 'worker' (go)? [y/N]: y

Removed target 'worker' from ./stoke.toml
Also delete the 'worker/' source directory? [y/N]: y
Deleted: ./worker
```

For scripts/CI, there's a non-interactive form too — it always leaves the source directory in place (never deletes files without a human in the loop):

```bash
stoke init --remove-target=worker --yes
```

---

## 5. Language cheat sheet

| Language | `stoke init --language=` | Build tool underneath | Version pin | Deps |
| --- | --- | --- | --- | --- |
| Python | `python` | pip / venv / conda | `python_version` in `stoke.toml` | stoke's own lock (`stoke.lock`) |
| Java | `java` | `javac` directly | `java_version` in `stoke.toml` | stoke's own lock, Maven Central for jars |
| C | `c` | gcc/clang | `c_standard` in `stoke.toml` | vcpkg |
| C++ | `cpp` | gcc/clang | `cpp_standard` in `stoke.toml` | vcpkg |
| Go | `go` | `go build`/`go run` | none | `go.sum` |
| Rust | `rust` | `cargo build --release`/run | optional `rust-toolchain.toml` | `Cargo.lock` |
| Kotlin | `kotlin` | Gradle (`gradlew` or system `gradle`) | `java_version` (enforced via `-Dorg.gradle.java.home`) | Gradle's own resolution |
| C# | `csharp` | `dotnet build`/`dotnet run` | optional `global.json` | NuGet (`dotnet` handles it) |
| Ruby | `ruby` | Bundler + `ruby` | optional `.ruby-version` | `Gemfile.lock` |
| PHP | `php` | Composer + `php` | optional `composer.json` `require.php` | `composer.lock` |
| JavaScript | `javascript` | Node.js (`npm install` + `node`) | none | `package-lock.json` |
| TypeScript | `typescript` | Node.js + tsx | none | `package-lock.json` |

`stoke install --language=<lang> --version=<v>` installs a toolchain (Python/Java/gcc/Go/Node.js) if you don't already have the right version:

```bash
stoke install --language=python --version=3.12
stoke install --language=python --list        # see what's available
stoke uninstall --language=python --version=3.12
```

C/C++ dependencies via vcpkg:

```bash
stoke install vcpkg                    # one-time setup
stoke vcpkg install fmt --target=myapp
stoke vcpkg list --target=myapp
stoke vcpkg remove fmt --target=myapp
```

---

## 6. Everyday commands

```bash
stoke build [target] [--force]        # --force ignores the cache, recompiles everything
stoke run [target]
stoke watch [target]                  # rebuilds on file changes
stoke hot-reload [target]             # rebuild + restart the running process
stoke clean [target] [--all]          # deletes build artifacts; --all also deletes the lock file
stoke ide-sync                        # regenerate VSCode/Eclipse/IntelliJ config files
```

**Build profiles (C/C++ only):**

```bash
stoke build --debug          # default
stoke build --release
stoke build --profile=asan   # custom profile, if you defined [profiles.asan] in stoke.toml
```

`stoke watch`/`stoke run`/`stoke hot-reload` accept the same `--debug`/`--release`/`--profile` flags. Other languages ignore them (no concept of build profiles).

---

## 7. Making it work for a team

### 7.1 One-line onboarding

Put this in your README or a setup script instead of a page of manual instructions:

```bash
stoke init --language=java --name=payments --version=21 --lock-mode=commit --yes
```

Every flag maps 1:1 to what the interactive wizard would have asked. Fails loudly (non-zero exit) instead of silently clobbering an existing `stoke.toml` unless `--yes` is passed.

### 7.2 Pin toolchain versions so "works on my machine" doesn't happen

| Language | File | Who reads it |
| --- | --- | --- |
| Python/Java | `python_version`/`java_version` in `stoke.toml` | stoke itself, checked at build time |
| C/C++ | `c_standard`/`cpp_standard` in `stoke.toml` | stoke itself |
| Kotlin | `java_version` in `stoke.toml` | stoke, enforced via `-Dorg.gradle.java.home` |
| Rust | `rust-toolchain.toml` | rustup, automatically |
| C# | `global.json` | dotnet CLI, automatically |
| Ruby | `.ruby-version` | rbenv/rvm/asdf/chruby, automatically |
| PHP | `composer.json`'s `require.php` | Composer, enforced on `composer install` |

Go/JavaScript/TypeScript have no pinning mechanism yet — rely on `go.mod`'s `go` directive / `engines` in `package.json` plus your own CI checks if you need this.

### 7.3 Reproducible builds

Set `lock_mode = "commit"` (the default from `stoke init`) so the lock file lives at the project root and gets committed to git — every teammate and CI runner resolves the exact same dependency versions. `lock_mode = "local"` keeps it gitignored under `.stoke/` instead, for per-developer flexibility.

### 7.4 Speed up builds — cache and parallelism

**Local cache** is automatic and content-hash based (a file with identical content skips recompilation even if its mtime changed — e.g. after a fresh `git checkout`).

**Shared/remote cache**, for C/C++ and Java, across your whole team or CI fleet — point everyone at the same network share/NAS path:

```bash
export STOKE_REMOTE_CACHE_DIR=/mnt/shared/stoke-cache      # or a mapped network drive on Windows
stoke build
```

One machine compiling something populates the shared cache; every other machine/CI runner with the same source and the same env var set gets a cache hit instead of recompiling. No cache-server to run — it's just a directory. Fails open: an unreachable or misconfigured directory silently falls back to normal local compilation, never breaks a build.

**Parallel multi-target builds:**

```bash
stoke build --all              # every target in stoke.toml, in parallel
stoke build --all --force      # same, ignoring cache
```

Capped by `project.jobs` in `stoke.toml` if set, otherwise CPU count. Output is grouped per-target (`=== name [OK|FAILED] ===`), printed in `stoke.toml` declaration order so logs stay reproducible across runs. One target failing doesn't stop the others — you get a full report and a non-zero exit if anything failed, except its own dependents, which are skipped rather than attempted (see below).

**Target dependencies:**

```toml
[targets.backend]
language = "python"
depends_on = ["shared_lib"]
```

`stoke build backend` builds `shared_lib` first automatically; `stoke build --all` builds independent targets in parallel but waits for each target's `depends_on` to finish before starting it. Unknown targets and dependency cycles are rejected when `stoke.toml` loads, before any build starts.

### 7.5 Locked-down / air-gapped networks

Point every network call stoke makes at an internal mirror instead of the public internet:

```bash
# Toolchain downloads (stoke install)
export STOKE_VERSION_API_BASE=https://internal-mirror.company.com/stoke-versions
# or per-invocation: stoke install --language=python --version=3.12 --base-url=https://internal-mirror.company.com/stoke-versions

# Java dependency downloads (stoke build)
export STOKE_MAVEN_REPO_URL=https://internal-mirror.company.com/maven2

# If the mirror requires auth (HTTP Basic):
export STOKE_VERSION_API_USER=ci
export STOKE_VERSION_API_PASSWORD=***
export STOKE_MAVEN_USER=ci
export STOKE_MAVEN_PASSWORD=***
```

Verified against a real Sonatype Nexus setup, both anonymous and authenticated. Every other language's dependency management already respects its own ecosystem's native mirror config transparently (`pip.conf`, `.npmrc`, `NuGet.config`, `.cargo/config.toml`, Bundler/Composer config, vcpkg registries) — nothing stoke-specific needed there.

---

## 8. Recommended setups by scenario

**Solo project / prototype:** `stoke init`, default `lock_mode=commit`, don't bother with any of the mirroring/cache env vars. Just `stoke build && stoke run`, `stoke watch` while iterating.

**Small team, single language:** same as above, plus put the `stoke init --language=... --yes` one-liner in your onboarding doc, and pin the language version so everyone's toolchain matches.

**Polyglot monorepo (a few services, different languages):** use the add-target flow (§4) to keep everything in one `stoke.toml`. Use `stoke build --all` in CI to build every service in one pass. If any of the services are Go/Rust/Kotlin/C#, make sure you're on a stoke version with the per-target scoping fix (§4) before relying on independent builds.

**CI pipeline:** non-interactive init isn't relevant here (the repo already has `stoke.toml`) but `stoke build --all --force` in CI (force to avoid trusting a stale cache from a previous run's checkout) combined with `STOKE_REMOTE_CACHE_DIR` pointed at a persistent cache volume gives you cross-run caching without any CI-specific cache configuration — same mechanism as the team's shared cache.

**Locked-down enterprise network:** set `STOKE_VERSION_API_BASE`/`STOKE_MAVEN_REPO_URL` (and the `_USER`/`_PASSWORD` auth pair if your mirror needs it) once in your CI environment and in a team-wide shell profile/onboarding doc. Combine with `lock_mode=commit` so dependency resolution never needs to reach out to the internet at all after the first `stoke build`.

---

## 9. When NOT to reach for stoke

- Large/complex C or C++ builds needing Meson, code generation, or a non-trivial build graph — stoke's own C/C++ model is intentionally simple (direct gcc/clang invocation + its own header tracking). If you already have a `CMakeLists.txt`, set `build_system = "cmake"` on that target instead: stoke delegates `build`/`run`/`watch`/`hot-reload`/`clean` to `cmake configure`/`--build` rather than driving the compiler itself.
- Windows C++ shops that specifically need MSVC — only gcc/clang (via MSYS2/MinGW) are supported.
- You need a plugin system to add a company-internal language or framework template without touching stoke's own source — doesn't exist yet.
- You're deep into Rust/Kotlin/C#/Ruby/PHP already at large scale — these five are the newest additions and are less battle-tested against large real-world codebases than the original seven languages.

---

## 10. Troubleshooting

- **Gradle (Kotlin) fails to even start**, with a cryptic error naming a JDK version: your system's default JDK may be too new/old for the Gradle version in use (e.g. Gradle 8.10 doesn't run on JDK 25). Point `JAVA_HOME` at a supported JDK just to run the `gradle`/`gradlew` CLI itself — this is separate from `java_version` in `stoke.toml`, which controls the JDK your *project* compiles against.
- **A print statement crashes with `UnicodeEncodeError` on Windows**: the Windows console's default codepage is locale-dependent (e.g. `cp949` on Korean-locale systems) and narrower than UTF-8 — non-ASCII characters (em-dashes, curly quotes, etc.) in any tool's console output can crash on some machines and not others. If you're extending stoke yourself, stick to ASCII in `print()` calls, or set `PYTHONIOENCODING=utf-8` / run `chcp 65001` first as a workaround.
- **A second Go/Rust/Kotlin/C# target isn't independently buildable**: you're likely on a stoke version older than the per-target scoping fix described in §4 — upgrade.
- **A remote/shared cache directory isn't helping**: confirm `STOKE_REMOTE_CACHE_DIR` is actually reachable from every machine with the exact same path (or equivalently mapped), and that the source content is byte-identical — the cache key is content-hash based, so even a whitespace difference is a miss, by design.
- **`stoke install`/`stoke build` (Java) fails with 401** against an internal mirror: set the matching `_USER`/`_PASSWORD` env var pair (`STOKE_VERSION_API_USER`/`PASSWORD` or `STOKE_MAVEN_USER`/`PASSWORD`) — the error message names which one is needed.

