# Rust

stoke supports Rust projects using the standard `cargo build` and `cargo run` tooling.

## Requirements

- Rust toolchain (`cargo`, `rustc`) via [rustup](https://rustup.rs)
- `stoke install --language=rust` is not supported yet — install Rust with rustup directly

## Configuration

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "rust"
```

That's it. Rust handles its own dependency management via `Cargo.toml`.

## How it works

- `stoke build` runs `cargo build --release --target-dir .stoke/rust/<target>`
- `stoke run` executes the compiled binary from that target directory
- Dependencies are managed by Cargo itself via `Cargo.toml` and `Cargo.lock`
- The binary name is read from `Cargo.toml`'s `[package] name` field

## Example

Create a new Rust project:

```bash
mkdir myapp
cd myapp
stoke init
```

Select `Rust` from the language menu. stoke will:

- Create `stoke.toml`
- Run `cargo init --name myapp --vcs none`
- Generate `src/main.rs` with a hello-world example

Then:

```bash
stoke build
stoke run
```

## Framework scaffolding

```bash
stoke init actix-web    # Actix-web — mature, high-performance framework
stoke init axum         # Axum — Tokio-based, from the Tokio team
stoke init rocket       # Rocket — ergonomics-focused framework
```

See [Frameworks](../../frameworks/en/overview.md) for details.

## Notes

- Builds always use `--release` (no separate debug profile)
- Cargo's own incremental cache handles rebuild skipping; `--force` is currently a no-op
- `target/` (Cargo's default build dir, unused by stoke) and `.stoke/` are added to `.gitignore`
