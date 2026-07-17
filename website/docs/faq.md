# FAQ

## General

### What is stoke?

A build tool that unifies workflows for Python, Java, C, and C++. One `stoke.toml` per project, one set of commands for all languages.

### Why not use language-specific tools?

Language-specific tools (pip, Maven, Make, Cargo) are excellent. But when you work across multiple languages, remembering which command builds what, configuring each ecosystem separately, and coordinating IDE setups becomes friction.

stoke provides a consistent interface without replacing the underlying tools. Under the hood, stoke uses pip, javac, Maven, gcc/clang, and vcpkg — it just wraps them consistently.

### Is stoke a replacement for CMake / Meson / Make?

Not really. stoke is more like a project runner than a build system. It's opinionated and works out of the box for common cases. For complex build scenarios (cross-compilation, code generation, custom build steps), you probably need CMake.

### What languages does stoke support?

Currently:

- Python
- Java (JDK 17+)
- C
- C++

More languages may come in the future.

### Which platforms?

- Windows (native installer)
- Linux (via pip)
- macOS (via pip)

Actively developed on Windows (MSYS2/MinGW64).

## Installation

### How do I update stoke?

Windows installer users: download the new installer and run it. It replaces the old version.

pip users: `pip install -U stoke-build`.

### How do I uninstall stoke?

Windows installer: use Windows "Add or Remove Programs" or run the uninstaller in the install directory.

pip: `pip uninstall stoke-build`.

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

Not directly. stoke doesn't support pre/post-build hooks yet. Wrap `stoke build` in a shell script if needed.

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

Not through stoke. stoke has its own simple build model. If you need CMake, use CMake directly.

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
RUN pip install stoke-build
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