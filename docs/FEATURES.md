# Feature status

What's verified, what's a known gap, and whether stoke fits a larger organization. See the [main README](../README.md) for how each feature works.

## Verified

- **Python, Java, C, C++** — the four original languages. Build, run, watch, hot-reload, IDE integration (VSCode/IntelliJ/Eclipse), build cache (content-hash + remote/shared cache), and lock files are all exercised end-to-end, including on Windows with MSVC (`compiler = "msvc"`) as well as gcc/clang.
- **Go, JavaScript, TypeScript** — build/run/watch/hot-reload and version pinning (`go.mod`, `.nvmrc`/`engines.node`) verified across their framework scaffolds (Gin, Echo, Fiber, Chi, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono).
- **Version pinning** — every language's pin mechanism (see the "Version pinning" bullet in the [main README](../README.md)) has been exercised for at least one project per language.
- **Private registry / mirror support** — verified against Sonatype Nexus (a `raw` hosted repo for the version JSON, and Nexus's `maven-central` proxy for Java deps), including Basic Auth.
- **Build cache** — content-hash invalidation verified to survive a fresh checkout (new mtimes, same content) correctly reusing cache entries; remote cache verified across two machines sharing a directory.
- **Pre/post-build hooks** — verified across `stoke build`, `stoke build --all`, `stoke watch`, and `stoke hot-reload` for every language.
- **Plugin system** (`stoke.languages` / `stoke.frameworks` entry points) — verified with a standalone example plugin package registering both entry point groups.
- **Multi-target projects** — adding and removing targets from an existing `stoke.toml` via `stoke init` verified for every language's project-root registration (Cargo workspace members, Gradle `settings.gradle.kts` includes, C#'s root `.csproj` excludes, etc.).
- **Target dependencies** (`depends_on`) — `stoke build`/`stoke build --all` verified to build dependencies first, run independent targets in parallel, reject cycles/unknown targets at load time, and skip (not attempt) targets whose dependency failed.
- **CMake delegation** (`build_system = "cmake"`) — verified end-to-end on Windows (MSVC/Visual Studio generator): `stoke build`/`run`/`clean` configure+build via `cmake`, locate the produced executable, and reuse `stoke watch`/`hot-reload`'s existing rebuild-and-restart loop unchanged.

## Known gaps

- No Meson integration for C/C++ (CMake is supported via `build_system = "cmake"`).
- Plugin-based languages don't get an automatic interactive `stoke init` wizard entry; a plugin needs its own `stoke.frameworks` entry point to support `stoke init` directly.
- Rust, Kotlin, C#, Ruby, PHP are the newest languages — command construction and templates are verified, but not yet battle-tested against large real-world projects in each ecosystem.
- Rails and Laravel scaffolds are intentionally omitted — both start via a CLI subcommand (`bin/rails server`, `php artisan serve`) rather than running an entry script directly, which doesn't fit stoke's run model.

## Fit for larger organizations

stoke covers the pieces a larger team usually needs: reproducible builds (lock files), team-wide toolchain version consistency (pinning across all 12 languages), a build cache that survives CI checkouts and can be shared across machines, private-registry/mirror support for locked-down networks, and dependency-ordered multi-target builds for monorepo-style projects. Pre/post-build hooks and the plugin system let a platform team extend it without forking.

The main thing to weigh before adopting it broadly: the five newest languages (Rust, Kotlin, C#, Ruby, PHP) haven't seen large real-world projects yet even though their code paths are exercised. This isn't an architectural blocker, but it's the area most likely to need a workaround today.
