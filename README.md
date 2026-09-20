<p align="center">
  <img src="docs/images/logo.png" alt="stoke" width="400">
</p>

<h2 align="center">Build, run, and scaffold projects in multiple languages.</h2>

Supports Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript (12 languages) with a single `stoke.toml`. Includes project scaffolding for Spring Boot, FastAPI, Flask, Django, and 21 other framework templates across Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript (Gin, Echo, Fiber, Chi, Bubble Tea, Actix Web, Axum, Rocket, Ktor, ASP.NET Core, Sinatra, Slim, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono).

## Installation

### Windows
Download the installer from [Releases](https://github.com/dvdsvds/stoke/releases/latest). Python is bundled — no prerequisites.

### macOS / Linux
Download `stoke-X.Y.Z-macos-<arch>.tar.gz` or `stoke-X.Y.Z-linux-<arch>.tar.gz` from [Releases](https://github.com/dvdsvds/stoke/releases/latest), extract it, and add it to your `PATH`. Python is bundled — no prerequisites.
```bash
tar xzf stoke-*.tar.gz
export PATH="$PWD/stoke:$PATH"
```
Not code-signed: on macOS, Gatekeeper will block the first run. Right-click (or Ctrl-click) the `stoke` binary, choose "Open", and confirm once.

### Verifying a download (optional)

Every release asset (the Windows installer and the macOS/Linux tarballs) is built by GitHub Actions and has a [build provenance attestation](https://docs.github.com/en/actions/security-guides/using-artifact-attestations-to-establish-provenance-for-builds) proving it was built from this repo's source by this repo's release workflow, not tampered with in between. Verify a downloaded file with the [GitHub CLI](https://cli.github.com):
```bash
gh attestation verify stoke-2.4.0-linux-x86_64.tar.gz --owner dvdsvds
```

## Quick Start

```bash
mkdir myapp
cd myapp
stoke init
stoke build
stoke run
```

## Features
- **Multi-language** — Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript with a single stoke.toml
- **Language installation** — install Python/JDK/gcc/Go/Node.js/Rust/C#/Ruby/PHP via `stoke install` (Kotlin has no separate toolchain — it builds through Gradle on top of a JDK)
- **Project scaffolding** — `stoke init <type>` for Spring Boot, FastAPI, Flask, Django, Gin, Echo, Fiber, Chi, Bubble Tea, Actix Web, Axum, Rocket, Ktor, ASP.NET Core, Sinatra, Slim, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono
- **Python environments** — venv or conda
- **Watch mode and hot-reload** for all languages
- **Build profiles** — debug/release and custom compile profiles for C/C++, including MSVC (`compiler = "msvc"`) alongside gcc/clang on Windows
- **Version pinning** — every language now has a pin mechanism, prompted during `stoke init` (e.g. Go's `go.mod` `go`/`toolchain` directives, Node's `.nvmrc` + `package.json` `engines.node`, Rust's `rust-toolchain.toml`) so every teammate and CI runner builds against the same version
- **Private registry / mirror support** — point toolchain installs and Java's Maven dependency downloads at an internal mirror, with optional Basic Auth
- **Build cache** — content-hash cache invalidation plus a shared/remote cache for C/C++ and Java, either a shared directory (`STOKE_REMOTE_CACHE_DIR`) or an HTTP cache server (`STOKE_REMOTE_CACHE_URL`, for remote teams/cloud CI without a shared filesystem)
- **CMake escape hatch for C/C++** — `build_system = "cmake"` on a C/C++ target delegates `build`/`run`/`watch`/`hot-reload`/`clean` to `cmake configure`/`--build` instead of stoke's own compile model, for projects with an existing `CMakeLists.txt`
- **Meson escape hatch for C/C++** — `build_system = "meson"` on a C/C++ target delegates `build`/`run`/`watch`/`hot-reload`/`clean` to `meson setup`/`meson compile` instead of stoke's own compile model, for projects with an existing `meson.build`
- **`stoke test`** — runs the target's tests via each ecosystem's standard tool: pytest/unittest (Python), JUnit 5 via a bundled console launcher (Java), `go test`, `cargo test`, `dotnet test`, `gradle test`, `npm test`, RSpec/rake, PHPUnit, and `ctest`/`meson test` for `build_system = "cmake"/"meson"`. For plain C/C++ builds, `test_sources` + a bundled single-header [doctest](https://github.com/doctest/doctest) (C++ only for now)
- **`stoke add`/`stoke remove`** — add or remove one or more dependencies at once. For Python/Java (where `stoke.toml` is the actual manifest) it edits `stoke.toml` and reinstalls; for JavaScript/TypeScript it runs `npm install`/`npm uninstall` directly (bypassing a known npm bug where it's needed) without touching `stoke.toml`, since `package.json` is the real manifest there; every other language points you at its native tool (`cargo add`, `go get`, etc.) instead
- **`stoke exec [--target=X] -- <command>`** — run a native tool command (`go mod tidy`, `cargo add`, `bundle add`, `composer require`, `dotnet add package`, ...) with the target's project-local toolchain on `PATH`, for when that language only lives in `.stoke/toolchains/` and isn't installed system-wide. Doesn't install anything — just finds what's already there and puts it on `PATH` for that one subprocess
- **`stoke audit [--target=X] [--json]`** — check the target's dependencies against known CVEs. Python and Java are checked directly against [OSV.dev](https://osv.dev) using the resolved versions in `stoke.lock`, no extra install needed. JavaScript/TypeScript, C#, and PHP use each ecosystem's built-in scanner (`npm audit`, `dotnet list package --vulnerable`, `composer audit`). Go, Rust, and Ruby delegate to `govulncheck`/`cargo-audit`/`bundler-audit` if installed (stoke tells you the install command if not). Not yet supported for Kotlin, C, or C++. `--json` prints machine-readable output for CI/dashboards — fully structured for Python/Java/JS/TS/PHP, a raw-output wrapper for the rest
- **`stoke outdated [--target=X] [--json]`** — check how far behind the latest available version each dependency is (staleness, independent of `stoke audit`'s CVE check). Same language coverage, mechanism, and `--json` support as `stoke audit` (PyPI/Maven Central queried directly for Python/Java, each ecosystem's native `outdated` command for the rest)
- **`stoke sbom [--target=X] [--format=cyclonedx|spdx] [--output=path]`** — generate a Software Bill of Materials for the target's resolved dependencies, as [CycloneDX](https://cyclonedx.org) (default) or [SPDX](https://spdx.dev) JSON. Supports Python and Java (from `stoke.lock`), Go (`go list -m`), Rust (`cargo metadata`), and JavaScript/TypeScript (`npm ls`). Writes `sbom.cdx.json`/`sbom.spdx.json` by default, or pass `--output=-` for stdout
- **`stoke doctor [--target=X] [--json]`** — fast, read-only environment diagnostic: entry/source files present, lock file exists and matches `stoke.toml`, toolchain reachable (PATH or project-local), venv installed packages match the lock file, `.gitignore` doesn't accidentally ignore a committed lock file. Doesn't install or build anything — just reports what's wrong, with a non-zero exit on any error
- **Pre/post-build hooks** — `pre_build`/`post_build` shell commands per target, for every language and every build path (`build`, `watch`, `hot-reload`)
- **Reproducible builds** via lock files
- **Auto IDE integration** (VSCode, IntelliJ, Eclipse)
- **Plugin system** — add a new language or `stoke init` scaffold from an external pip package via entry points, no stoke source changes needed
- **Monorepos** — `stoke init --workspace` creates a root `stoke.toml` with no language/target, just a members list; `stoke new <name> -l <language> [-V <version>]` adds a service as its own subdirectory with an independent `stoke.toml`/`stoke.lock` (registered into the root's members automatically) — safe even when two services use the same language at different versions. `stoke build --all`/`stoke test --all`, run at the workspace root, build/test every member in sequence, continuing past a failed member and reporting which ones failed at the end
- **`stoke self-update [--check] [--yes]`** — update the standalone binary to the latest GitHub release in place. Linux/macOS swap the install directory atomically (with rollback on failure); Windows launches the installer silently in the background. Only works for the standalone binary distribution, not a `pip install -e .` source checkout
- **`stoke completions <bash|zsh|fish>`** — prints a shell completion script generated from stoke's actual command/flag structure (so it can't drift out of sync). Completes target names dynamically by reading the current directory's `stoke.toml`

## Build hooks

Every target can declare `pre_build`/`post_build` — shell commands to run before/after the language-specific build step:

```toml
[targets.myapp]
language = "python"
pre_build = ["echo starting build"]
post_build = ["cp dist/myapp ./release/myapp"]
```

Commands run through the shell (pipes/env vars/multiple args all work), in declared order, and apply the same way to `stoke build`, `stoke watch`, and `stoke hot-reload`. If any `pre_build` command exits non-zero, the language build itself never starts; a failing `post_build` command fails the whole build too.

**Security note**: `pre_build`/`post_build` execute whatever string is in `stoke.toml`, verbatim, through the shell. Running `stoke build` (or `--all`/`watch`/`hot-reload`) on a project means running arbitrary commands from that project's `stoke.toml` with your user's permissions — **don't clone an untrusted repository and build it right away.** Check the `pre_build`/`post_build` values first.

## Documentation

Full documentation: [https://dvdsvds.github.io/stoke/](https://dvdsvds.github.io/stoke/)

Also available in the repo:
- [How To Use guide](./docs/HOW_TO_USE.md) ([한국어](./docs/HOW_TO_USE_KO.md))
- [한국어 README](./docs/README_ko.md)
- [Full feature status](./docs/FEATURES.md) ([한국어](./docs/FEATURES.ko.md)) — what's verified, known gaps, and whether stoke fits a larger org
- [CI/CD examples](./docs/ci/) — GitHub Actions workflow and Dockerfile for building/testing/auditing a stoke project in CI

## License

MIT