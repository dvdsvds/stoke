# FAQ

## General

### What is stoke?

A build tool that unifies workflows for Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, and TypeScript. One `stoke.toml` per project, one set of commands for all languages.

### Why not use language-specific tools?

Language-specific tools (pip, Maven, Make, Cargo) are excellent. But when you work across multiple languages, remembering which command builds what, configuring each ecosystem separately, and coordinating IDE setups becomes friction.

stoke provides a consistent interface without replacing the underlying tools. Under the hood, stoke uses pip, javac, Maven, gcc/clang, vcpkg, `go build`, and npm — it just wraps them consistently.

### Is stoke a replacement for CMake / Meson / Make?

Not really. stoke is more like a project runner than a build system. It's opinionated and works out of the box for common cases. For a C/C++ target with an existing `CMakeLists.txt`, set `build_system = "cmake"` and stoke delegates to `cmake` instead of driving the compiler itself — see [stoke.toml reference](configuration/stoke-toml.md#cmake-for-cc). For build scenarios CMake itself doesn't cover well, or for Meson, you're on your own.

### What languages does stoke support?

Currently:

- Python
- Java (JDK 17+)
- C
- C++
- Go
- Rust
- Kotlin (via Gradle)
- C# (via the .NET SDK)
- Ruby
- PHP
- JavaScript
- TypeScript

More languages may come in the future.

### Which platforms?

- Windows (native installer)
- Linux (native tarball)
- macOS (native tarball)

Actively developed on Windows (MSYS2/MinGW64).

## Installation

### How do I update stoke?

Windows installer users: download the new installer and run it. It replaces the old version.

macOS/Linux tarball users: download the new tarball from [Releases](https://github.com/dvdsvds/stoke/releases/latest) and extract it over the old one.

### How do I uninstall stoke?

Windows installer: use Windows "Add or Remove Programs" or run the uninstaller in the install directory.

macOS/Linux: delete the extracted `stoke` folder and remove it from your `PATH`.

## Configuration

### Can I have multiple targets in one project?

Yes. Any number of `[targets.<name>]` sections:

```toml
[targets.server]
language = "python"
entry = "server/main.py"

[targets.client]
language = "cpp"
sources = ["client/**/*.cpp"]
```

Build all: `stoke build`  
Build one: `stoke build server`

### Can targets use different languages?

Yes. Each target has its own `language`.

### Can one target depend on another?

Yes, with `depends_on`:

```toml
[targets.backend]
language = "python"
depends_on = ["shared_lib"]
```

`stoke build backend` builds `shared_lib` first. `stoke build --all` builds independent targets in parallel but waits for each target's dependencies to finish first, and skips a target if its dependency failed. Cycles and references to unknown targets are rejected when `stoke.toml` loads.

### Can I share code between targets?

Yes. Adjust `sources` glob patterns to include shared code:

```toml
[targets.server]
language = "python"
sources = ["server/**/*.py", "shared/**/*.py"]

[targets.worker]
language = "python"
sources = ["worker/**/*.py", "shared/**/*.py"]
```

### Where's my build output?

`.stoke/{language}/{target}/{profile}/`. See [`stoke build`](commands/build.md#output-structure).

### Can I add custom build steps?

Yes — `pre_build`/`post_build` on any target run shell commands before/after that target's build. See [stoke.toml reference](configuration/stoke-toml.md#build-hooks). They run through the shell with your user's permissions, so only build `stoke.toml` files you trust.

## Language-specific

### Python: does stoke replace pip / venv?

No. stoke uses venv and pip under the hood. It automates the venv creation, dependency installation, and PYTHONPATH setup.

### Java: does stoke use Maven?

stoke uses Maven Central for dependency downloads. It doesn't use Maven's build system — it invokes `javac` directly.

The generated `pom.xml` is for IDE integration only.

### C/C++: what compiler does stoke use?

- Linux default: gcc
- macOS default: clang
- Windows default: gcc (from MSYS2/MinGW)

Override with build profiles. MSVC (`cl.exe`) is not currently supported.

### C/C++: can I use CMake?

Yes — set `build_system = "cmake"` on the target and point `source_dir` at the folder with `CMakeLists.txt`. stoke then runs `cmake` configure/build instead of its own compile model; `c_standard`/`cpp_standard` and profile compile flags are ignored on this path since `CMakeLists.txt` owns them. See [stoke.toml reference](configuration/stoke-toml.md#cmake-for-cc).

### Rust, Kotlin, C#, Ruby, PHP: does stoke replace Cargo / Gradle / dotnet / Bundler / Composer?

No. stoke delegates directly to each ecosystem's own tool — `cargo build`/`cargo run` for Rust, `gradlew build`/`gradlew run` for Kotlin, `dotnet build`/`dotnet run` for C#, `bundle install` + `ruby`/`bundle exec ruby` for Ruby, `composer install` + `php` for PHP. stoke just gives them a consistent `stoke build`/`stoke run` interface alongside the other languages.

### Why don't Rails and Laravel have `stoke init` scaffolds?

Both start via a CLI subcommand (`bin/rails server`, `php artisan serve`) rather than by directly executing an entry script, which doesn't fit stoke's current run model (`stoke run` executes one script/binary). Sinatra (Ruby) and Slim (PHP) were added instead since they fit that model — see the [Ruby](languages/en/ruby.md) and [PHP](languages/en/php.md) language pages for details.

## Behavior

### Why is my build not using the cache?

Common reasons:

- Header changed (C/C++ tracks headers automatically)
- Source file's timestamp changed
- Compile flags changed (different profile)
- `--force` was used

Verbose mode may help debug:

```bash
stoke build -v
```

### Why does `stoke build` regenerate IDE files every time?

It doesn't — since v0.7.2. IDE files are only rewritten when their content changes.

If you see `IDE files updated: X, Y`, only those actually changed.

### Why is `Lock file saved` showing every time?

Fixed in v0.7.2. Update to the latest version.

## Integration

### Does stoke work in CI?

Yes. `stoke build` in a container or CI runner works the same as locally. Cache the `.stoke/` directory to speed up subsequent builds.

Recommended: use `lock_mode = "strict"` in CI for reproducible builds.

### Does stoke work with Docker?

Yes. Install stoke in the Dockerfile:

```dockerfile
RUN curl -fsSL -o stoke.tar.gz \
      https://github.com/dvdsvds/stoke/releases/latest/download/stoke-X.Y.Z-linux-x86_64.tar.gz \
    && tar xzf stoke.tar.gz -C /opt \
    && ln -s /opt/stoke/stoke /usr/local/bin/stoke
```

Then `stoke build` normally.

### Can I use stoke as a subprocess from another tool?

Yes. Exit codes are meaningful:

- 0: success
- non-zero: failure

Output goes to stdout/stderr in the standard way.

## Contributing

### How can I contribute?

- Report bugs or request features: [github.com/dvdsvds/stoke/issues](https://github.com/dvdsvds/stoke/issues)
- Pull requests welcome on GitHub

### Where's the source code?

[github.com/dvdsvds/stoke](https://github.com/dvdsvds/stoke)

MIT license.

## Related

- [Troubleshooting](troubleshooting.md)
- [Getting Started](getting-started/installation.md)