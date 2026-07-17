# Lock File

`.stoke/lock.toml` records the exact versions of tools and dependencies used in each build. It ensures reproducibility: another developer (or CI) building your project gets the same versions.

## Purpose

- **Reproducibility**: same versions across machines
- **Speed**: skip re-resolving dependencies if lock matches
- **Auditability**: see exactly what versions your build uses

## Location
myproject/
├── stoke.toml
└── .stoke/
└── lock.toml       # ← lock file

## Should you commit it?

**Yes for applications**, no for libraries.

- **Application**: commit `lock.toml` to git. This pins versions so all developers and CI use the same versions.
- **Library**: don't commit. Let users of the library resolve fresh versions.

Add to `.gitignore` for libraries:
.stoke/lock.toml
