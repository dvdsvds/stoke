# stoke — How To Use (v1.5.1)

A practical guide: how to actually use stoke day to day, what setups it's good for, and concrete commands for each scenario.

## TL;DR

```bash
mkdir myapp && cd myapp
stoke init      # pick a language, answer a few prompts
stoke build     # compile/prepare
stoke run       # run it
```

One `stoke.toml` per project, one target per project (see §8 if you need more than one build target). One CLI for build/run/watch/scaffold across 12 languages. `stoke init` writes the initial file for you; settings beyond what it prompts for (`include_dirs`, `pre_build`/`post_build`, custom `[profiles.*]`, etc.) are edited by hand.

---

## 1. Is stoke a good fit for what you're building?

**Good fit:**
- A small-to-medium project or a team of roughly 10–30 people.
- A single service or app in any of the 12 supported languages, where you'd like one consistent `build`/`run`/`watch` command instead of learning each language's own tool.
- Teams onboarding new members often and wanting a single `stoke init --language=... --yes` line to replace a wiki page of manual setup steps.
- Projects that want reproducible builds (a committed lock file) without adopting a heavier tool (Bazel, Nx, Turborepo) and its learning curve.
- Environments where you already use a specific toolchain per language (Cargo, Gradle, `dotnet`, Bundler, Composer, npm, Maven Central) — stoke delegates to them rather than reinventing dependency resolution, so you keep using `Cargo.toml`/`build.gradle.kts`/etc. as normal.

**Not a good fit (see §8 for the full list):**
- Large C/C++ codebases needing a generated build graph beyond CMake/Meson (both are supported via `build_system = "cmake"`/`"meson"` — see §8 below).
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
                           # bubbletea, actix-web, axum, rocket, ktor, spring-boot-kotlin,
                           # aspnet-core, sinatra, slim, express, fastify,
                           # nextjs, nestjs, vite, nuxt, sveltekit, hono
```

---

## 4. Language cheat sheet

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

## 5. Everyday commands

```bash
stoke build [target] [--force]        # --force ignores the cache, recompiles everything
stoke run [target]
stoke watch [target]                  # rebuilds on file changes
stoke hot-reload [target]             # rebuild + restart the running process
stoke clean [target] [--all]          # deletes build artifacts; --all also deletes the lock file
stoke ide-sync                        # regenerate VSCode/Eclipse/IntelliJ config files
stoke exec [--target=X] -- <command>  # run a command with the target's project-local toolchain on PATH
```

**`stoke exec`** — `stoke install`/`stoke init` install language toolchains into `.stoke/toolchains/` without touching your system PATH, so `stoke build`/`run` work even if the language isn't installed system-wide, but a native tool command you type yourself (`go mod tidy`, `cargo add serde`, `bundle add rails`, `composer require monolog/monolog`, `dotnet add package Newtonsoft.Json`) only looks at PATH and fails if that's the only place the language lives. `stoke exec` runs the given command with that project-local toolchain's `bin/` prepended to PATH (and, for Rust, `RUSTUP_HOME`/`CARGO_HOME` set) instead:

```bash
stoke exec -- go mod tidy
stoke exec --target=api -- cargo add serde
```

`stoke init` asks which IDE to integrate with for Python/Java/C/C++ projects (`vscode`, the default, writes `.vscode/settings.json` plus `compile_commands.json`/`c_cpp_properties.json` for C/C++; `eclipse` writes `.classpath`/`.project` for Java; `intellij` writes `pom.xml` for Java, or just `compile_commands.json` for C/C++ (also what CLion, clangd, and clangd-based Vim/Neovim/Emacs setups read directly); `none` writes nothing on every `stoke build`). It's stored as `ide = "..."` under `[project]` in `stoke.toml` — edit it by hand any time. This is separate from `stoke ide-sync` above, which always generates a VSCode multi-root workspace file across every stoke project it finds, regardless of this setting.

**Build profiles (C/C++ only):**

```bash
stoke build --debug          # default
stoke build --release
stoke build --profile=asan   # custom profile, if you defined [profiles.asan] in stoke.toml
```

`stoke watch`/`stoke run`/`stoke hot-reload` accept the same `--debug`/`--release`/`--profile` flags. Other languages ignore them (no concept of build profiles).

---

## 6. Making it work for a team

### 6.1 One-line onboarding

Put this in your README or a setup script instead of a page of manual instructions:

```bash
stoke init --language=java --name=payments --version=21 --lock-mode=commit --yes
```

Every flag maps 1:1 to what the interactive wizard would have asked. Fails loudly (non-zero exit) instead of silently clobbering an existing `stoke.toml` unless `--yes` is passed.

### 6.2 Pin toolchain versions so "works on my machine" doesn't happen

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

### 6.3 Reproducible builds

Set `lock_mode = "commit"` (the default from `stoke init`) so the lock file lives at the project root and gets committed to git — every teammate and CI runner resolves the exact same dependency versions. `lock_mode = "local"` keeps it gitignored under `.stoke/` instead, for per-developer flexibility.

### 6.4 Speed up builds — cache and parallelism

**Local cache** is automatic and content-hash based (a file with identical content skips recompilation even if its mtime changed — e.g. after a fresh `git checkout`).

**Shared/remote cache**, for C/C++ and Java, across your whole team or CI fleet — point everyone at the same network share/NAS path:

```bash
export STOKE_REMOTE_CACHE_DIR=/mnt/shared/stoke-cache      # or a mapped network drive on Windows
stoke build
```

One machine compiling something populates the shared cache; every other machine/CI runner with the same source and the same env var set gets a cache hit instead of recompiling. No cache-server to run — it's just a directory. Fails open: an unreachable or misconfigured directory silently falls back to normal local compilation, never breaks a build.

**Remote team / cloud CI without a shared network drive** — point at an HTTP cache server instead:

```bash
export STOKE_REMOTE_CACHE_URL=https://cache.mycompany.com
export STOKE_REMOTE_CACHE_USER=ci       # optional, HTTP Basic Auth
export STOKE_REMOTE_CACHE_PASSWORD=***
stoke build
```

Same cache keys, same fail-open behavior (an unreachable/misconfigured server or a failed upload just falls back to local compilation) — this is a drop-in alternative to `STOKE_REMOTE_CACHE_DIR` for teams without a shared filesystem (remote workers, GitHub-hosted CI runners, etc). If both are set, `STOKE_REMOTE_CACHE_URL` wins. The server just needs to answer `GET`/`PUT` on `/objects/<key>` and `/dirs/<key>.tar` with the bytes stoke sends it — stoke doesn't ship a server implementation.

**Parallel file compilation** (C/C++ only): multiple source files in one target compile in parallel automatically, capped by `project.jobs` in `stoke.toml` if set, otherwise CPU count.

### 6.5 Locked-down / air-gapped networks

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

### 6.6 CI/CD

stoke ships as a standalone binary (Python bundled in), so a CI runner or Docker build stage needs no pre-installed language runtime just to run stoke itself — download the release tarball, put it on `PATH`, and `stoke build`/`stoke test`/`stoke audit` work the same as on your machine.

- [`docs/ci/github-actions.yml`](./ci/github-actions.yml) — installs stoke, restores the shared build cache (section 6.4) across runs via `actions/cache`, then runs build/test/audit.
- [`docs/ci/Dockerfile`](./ci/Dockerfile) — multi-stage build: stoke + the pinned language toolchain compile the project in the build stage, only the compiled output ships in the runtime image.

`stoke audit` is CI-friendly by design: it exits non-zero when a known CVE is found in a resolved dependency, so wiring it into a required check gates merges on it directly.

### 6.7 Monorepos

A single `stoke.toml` supports only one target per language (its lock file has one version slot per language, not one per target), so two same-language services in one file would clobber each other's lock data. Instead, give each service its own subdirectory with its own independent `stoke.toml`/`stoke.lock`, tied together by a workspace root:

```bash
mkdir my-company && cd my-company
stoke init --workspace --name=my-company   # root stoke.toml: no language/target, just a members list

stoke new backend -l python -V 3.12
stoke new worker  -l python -V 3.11        # different Python version than backend -- no conflict
stoke new frontend -l typescript
```

```
my-company/
├── stoke.toml           # [workspace] members = ["backend", "worker", "frontend"]
├── backend/
│   ├── stoke.toml        # independent config, python_version = "3.12"
│   └── stoke.lock
├── worker/
│   ├── stoke.toml        # python_version = "3.11"
│   └── stoke.lock
└── frontend/
    └── stoke.toml
```

Each service builds exactly like a standalone project — `cd backend && stoke build`. `stoke new` run inside the workspace root registers the new service into the root's `members` list automatically; run outside one, it just creates the subdirectory with no workspace involved.

From the root, `stoke build --all` and `stoke test --all` build/test every member in sequence -- each in its own subdirectory, with its own `stoke.toml`. A failed member doesn't stop the rest; at the end, stoke prints which members failed and exits non-zero if any did:

```bash
cd my-company
stoke build --all
# === backend ===
# Build complete: backend
#
# === worker ===
# Build complete: worker
#
# All 2 member(s) succeeded.
```

---

## 7. Recommended setups by scenario

**Solo project / prototype:** `stoke init`, default `lock_mode=commit`, don't bother with any of the mirroring/cache env vars. Just `stoke build && stoke run`, `stoke watch` while iterating.

**Small team, single language:** same as above, plus put the `stoke init --language=... --yes` one-liner in your onboarding doc, and pin the language version so everyone's toolchain matches.

**Polyglot monorepo (a few services, different languages):** give each service its own `stoke.toml` in its own directory rather than trying to combine them into one project — stoke is a single-target-per-project tool.

**CI pipeline:** non-interactive init isn't relevant here (the repo already has `stoke.toml`) but `stoke build --force` in CI (force to avoid trusting a stale cache from a previous run's checkout) combined with `STOKE_REMOTE_CACHE_DIR` pointed at a persistent cache volume gives you cross-run caching without any CI-specific cache configuration — same mechanism as the team's shared cache.

**Locked-down enterprise network:** set `STOKE_VERSION_API_BASE`/`STOKE_MAVEN_REPO_URL` (and the `_USER`/`_PASSWORD` auth pair if your mirror needs it) once in your CI environment and in a team-wide shell profile/onboarding doc. Combine with `lock_mode=commit` so dependency resolution never needs to reach out to the internet at all after the first `stoke build`.

---

## 8. When NOT to reach for stoke

- Large/complex C or C++ builds needing code generation or a non-trivial build graph beyond what CMake/Meson delegation covers — stoke's own C/C++ model is intentionally simple (direct gcc/clang invocation + its own header tracking). If you already have a `CMakeLists.txt` or `meson.build`, set `build_system = "cmake"` or `build_system = "meson"` on that target instead: stoke delegates `build`/`run`/`watch`/`hot-reload`/`clean` to `cmake configure`/`--build` or `meson setup`/`compile` rather than driving the compiler itself.
- Windows C++ shops that specifically need MSVC — only gcc/clang (via MSYS2/MinGW) are supported.
- You need a plugin system to add a company-internal language or framework template without touching stoke's own source — doesn't exist yet.
- You're deep into Rust/Kotlin/C#/Ruby/PHP already at large scale — these five are the newest additions and are less battle-tested against large real-world codebases than the original seven languages.
- You need multiple build targets (e.g. a backend + a worker) managed from one `stoke.toml` — stoke is single-target-per-project; give each one its own `stoke.toml` in its own directory instead.

---

## 9. Troubleshooting

- **Gradle (Kotlin) fails to even start**, with a cryptic error naming a JDK version: your system's default JDK may be too new/old for the Gradle version in use (e.g. Gradle 8.10 doesn't run on JDK 25). Point `JAVA_HOME` at a supported JDK just to run the `gradle`/`gradlew` CLI itself — this is separate from `java_version` in `stoke.toml`, which controls the JDK your *project* compiles against.
- **A print statement crashes with `UnicodeEncodeError` on Windows**: the Windows console's default codepage is locale-dependent (e.g. `cp949` on Korean-locale systems) and narrower than UTF-8 — non-ASCII characters (em-dashes, curly quotes, etc.) in any tool's console output can crash on some machines and not others. If you're extending stoke yourself, stick to ASCII in `print()` calls, or set `PYTHONIOENCODING=utf-8` / run `chcp 65001` first as a workaround.
- **A remote/shared cache directory isn't helping**: confirm `STOKE_REMOTE_CACHE_DIR` is actually reachable from every machine with the exact same path (or equivalently mapped), and that the source content is byte-identical — the cache key is content-hash based, so even a whitespace difference is a miss, by design.
- **`stoke install`/`stoke build` (Java) fails with 401** against an internal mirror: set the matching `_USER`/`_PASSWORD` env var pair (`STOKE_VERSION_API_USER`/`PASSWORD` or `STOKE_MAVEN_USER`/`PASSWORD`) — the error message names which one is needed.

