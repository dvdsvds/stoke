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

## Known gaps

- No macOS/Linux native installer yet (pip works, but isn't verified end-to-end) — Windows has the bundled installer.
- No CMake/Meson integration for C/C++ — stoke has its own simple build model, so large/generated C/C++ build graphs don't fit.
- Plugin-based languages don't get an automatic interactive `stoke init` wizard entry; a plugin needs its own `stoke.frameworks` entry point to support `stoke init` directly.
- Rust, Kotlin, C#, Ruby, PHP are the newest languages — command construction and templates are verified, but not yet battle-tested against large real-world projects in each ecosystem.
- No inter-target dependency graph — `stoke build --all` treats every target as independent.
- Rails and Laravel scaffolds are intentionally omitted — both start via a CLI subcommand (`bin/rails server`, `php artisan serve`) rather than running an entry script directly, which doesn't fit stoke's run model.

## Fit for larger organizations

stoke covers the pieces a larger team usually needs: reproducible builds (lock files), team-wide toolchain version consistency (pinning across all 12 languages), a build cache that survives CI checkouts and can be shared across machines, and private-registry/mirror support for locked-down networks. Pre/post-build hooks and the plugin system let a platform team extend it without forking.

The main things to weigh before adopting it broadly: no macOS/Linux installer yet (pip works but isn't the polished path), no dependency graph between targets in a monorepo-style multi-target project, and the five newest languages (Rust, Kotlin, C#, Ruby, PHP) haven't seen large real-world projects yet even though their code paths are exercised. None of these are architectural blockers, but they're the areas most likely to need a workaround today.
