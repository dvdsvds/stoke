# Contributing to stoke

## Bug reports

Open an issue with:
- Your OS/architecture and `stoke --version`
- The exact command you ran and its full output
- Your `stoke.toml` (redact anything sensitive)

## Feature requests

Open an issue describing the use case, not just the feature — what are you trying to do that stoke can't do today? Check [docs/FEATURES.md](./docs/FEATURES.md) first; it lists known gaps that might already cover what you're after.

## Development setup

```bash
git clone https://github.com/dvdsvds/stoke.git
cd stoke
pip install -e .
stoke --help
```

No build step — it's a pure Python package, `pip install -e .` gives you a live `stoke` command backed by the checkout.

## Adding a language or framework

stoke has a plugin system for exactly this — see the "Plugin system" entry in [README.md](./README.md) and the `stoke.languages`/`stoke.frameworks` entry points. A plugin doesn't require changing stoke's source at all; if what you're adding is broadly useful, feel free to open a PR against this repo directly instead.

## Pull requests

- Keep PRs focused — one language/feature/fix per PR is easier to review than a bundle.
- If you're fixing a bug, a minimal repro (a `stoke.toml` + steps) in the PR description helps a lot.
- Run the relevant `stoke` commands against a real scaffolded project before opening the PR — this repo doesn't have an automated test suite yet, so manual verification is the bar.

## Documentation

Non-obvious design decisions and bug investigations get written up under [`docs/report/`](./docs/report/), one file per change (`YYYY-MM-DD HH-MM [tag] title.md`). Not required for every PR, but if you're fixing something subtle, a short writeup there helps future contributors understand why.
