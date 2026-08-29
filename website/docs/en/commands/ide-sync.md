# stoke ide-sync

Generate IDE configurations for a multi-project workspace.

## Usage

Run from a directory that contains multiple stoke projects:

```bash
stoke ide-sync
```

## What it does

Scans subdirectories for `stoke.toml` files and generates:

- `.vscode/settings.json` — VSCode workspace settings
- `{workspace_name}.code-workspace` — VSCode multi-root workspace file

## Example

Directory structure:
myworkspace/
├── frontend/
│   └── stoke.toml       # python
├── backend/
│   └── stoke.toml       # java
└── engine/
└── stoke.toml       # cpp

Run:
$ cd myworkspace
$ stoke ide-sync
Scanning for stoke projects under C:\Users...\myworkspace...
Found 3 project(s):
[python] frontend
[java] backend
[cpp] engine
Generated: C:\Users...\myworkspace.vscode\settings.json
Generated: C:\Users...\myworkspace\myworkspace.code-workspace
Open in VSCode: C:\Users...\myworkspace\myworkspace.code-workspace

Open the `.code-workspace` file in VSCode to work on all projects together with proper language support for each.

## Individual project IDE files

`stoke build` also generates per-project IDE files (VSCode settings, Eclipse `.classpath`, `pom.xml`, etc.). Those are separate from `ide-sync`.

- **stoke build** — per-project IDE files (single project)
- **stoke ide-sync** — workspace-level VSCode setup (multiple projects)

## Related

- [IDE Integration](../advanced/ide-integration.md) — deep dive