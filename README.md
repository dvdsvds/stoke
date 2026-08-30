<p align="center">
  <img src="docs/images/logo.png" alt="stoke" width="400">
</p>

<h2 align="center">Build, run, and scaffold projects in multiple languages.</h2>

Supports Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript (12 languages) with a single `stoke.toml`. Includes project scaffolding for Spring Boot, FastAPI, Flask, Django, and 20 other web framework templates across Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript (Gin, Echo, Fiber, Chi, Actix Web, Axum, Rocket, Ktor, ASP.NET Core, Sinatra, Slim, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono).

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
- **Language installation** — install Python/JDK/gcc/Go/Node.js via `stoke install` (Rust/Kotlin/C#/Ruby/PHP delegate to their own installers)
- **Project scaffolding** — `stoke init <type>` for Spring Boot, FastAPI, Flask, Django, Gin, Echo, Fiber, Chi, Actix Web, Axum, Rocket, Ktor, ASP.NET Core, Sinatra, Slim, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono
- **Python environments** — venv or conda
- **Watch mode and hot-reload** for all languages
- **Build profiles** — debug/release and custom compile profiles for C/C++, including MSVC (`compiler = "msvc"`) alongside gcc/clang on Windows
- **Version pinning** — every language now has a pin mechanism, prompted during `stoke init` (e.g. Go's `go.mod` `go`/`toolchain` directives, Node's `.nvmrc` + `package.json` `engines.node`, Rust's `rust-toolchain.toml`) so every teammate and CI runner builds against the same version
- **Private registry / mirror support** — point toolchain installs and Java's Maven dependency downloads at an internal mirror, with optional Basic Auth
- **Build cache** — content-hash cache invalidation plus a shared/remote cache for C/C++ and Java
- **Parallel multi-target builds** — `stoke build --all`, and `stoke init` can add or remove a target from an existing project
- **Target dependencies** — `depends_on = ["other_target"]` on a target; `stoke build`/`stoke build --all` build dependencies first and respect the order (cycles and unknown targets are rejected at load time)
- **CMake escape hatch for C/C++** — `build_system = "cmake"` on a C/C++ target delegates `build`/`run`/`watch`/`hot-reload`/`clean` to `cmake configure`/`--build` instead of stoke's own compile model, for projects with an existing `CMakeLists.txt`
- **Meson escape hatch for C/C++** — `build_system = "meson"` on a C/C++ target delegates `build`/`run`/`watch`/`hot-reload`/`clean` to `meson setup`/`meson compile` instead of stoke's own compile model, for projects with an existing `meson.build`
- **Pre/post-build hooks** — `pre_build`/`post_build` shell commands per target, for every language and every build path (`build`, `build --all`, `watch`, `hot-reload`)
- **Reproducible builds** via lock files
- **Auto IDE integration** (VSCode, IntelliJ, Eclipse)
- **Plugin system** — add a new language or `stoke init` scaffold from an external pip package via entry points, no stoke source changes needed

## Build hooks

Every target can declare `pre_build`/`post_build` — shell commands to run before/after the language-specific build step:

```toml
[targets.myapp]
language = "python"
pre_build = ["echo starting build"]
post_build = ["cp dist/myapp ./release/myapp"]
```

Commands run through the shell (pipes/env vars/multiple args all work), in declared order, and apply the same way to `stoke build`, `stoke build --all`, `stoke watch`, and `stoke hot-reload`. If any `pre_build` command exits non-zero, the language build itself never starts; a failing `post_build` command fails the whole build too.

**Security note**: `pre_build`/`post_build` execute whatever string is in `stoke.toml`, verbatim, through the shell. Running `stoke build` (or `--all`/`watch`/`hot-reload`) on a project means running arbitrary commands from that project's `stoke.toml` with your user's permissions — **don't clone an untrusted repository and build it right away.** Check the `pre_build`/`post_build` values first.

## Documentation

Full documentation: [https://dvdsvds.github.io/stoke/](https://dvdsvds.github.io/stoke/)

Also available in the repo:
- [How To Use guide](./docs/HOW_TO_USE.md) ([한국어](./docs/HOW_TO_USE_KO.md))
- [한국어 README](./docs/README_ko.md)
- [Full feature status](./docs/FEATURES.md) ([한국어](./docs/FEATURES.ko.md)) — what's verified, known gaps, and whether stoke fits a larger org

## License

MIT