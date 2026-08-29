# IDE Integration

stoke generates IDE configuration files automatically during `stoke build`. Open your project in the IDE — everything just works.

## Supported IDEs

| IDE | Python | Java | C/C++ |
|-----|--------|------|-------|
| VSCode | ✓ | ✓ | ✓ |
| Eclipse | | ✓ | |
| IntelliJ / JetBrains | | ✓ (via Maven) | |
| clangd-based | | | ✓ |

## VSCode

### Files generated

Per-project (in project root):

- `.vscode/settings.json`

For C/C++:
- `.vscode/c_cpp_properties.json` (Microsoft C/C++ extension)
- `compile_commands.json` (clangd, Native Debug)

For Java:
- `.classpath` (Eclipse format, used by VSCode Java extension)
- `.project` (Eclipse format)
- `pom.xml` (Maven format)

### Settings

`settings.json` includes:

- **Python**: interpreter path, extra paths, exclusions
- **Java**: source paths, referenced JARs
- **C/C++**: include paths, defines, compiler path

Also excludes `.stoke/` from file watching to reduce editor lag.

### Extensions

Recommended VSCode extensions:

- **Python** — Microsoft Python extension
- **Java** — Extension Pack for Java
- **C/C++** — Microsoft C/C++ extension OR clangd

## Eclipse (Java)

Import as an existing Eclipse project:

1. File → Import → General → Existing Projects into Workspace
2. Select the project folder

Eclipse reads `.classpath` and `.project`.

## IntelliJ / JetBrains (Java)

Import as a Maven project:

1. File → Open → select the project folder or `pom.xml`
2. IntelliJ reads `pom.xml`

## clangd (C/C++)

`compile_commands.json` at the project root is the standard for clangd-based tools:

- clangd LSP server
- CLion (via clangd)
- Neovim + clangd
- Emacs + clangd
- Any editor with clangd support

No extra config needed. Just open the project.

## Multi-project workspaces

For a repository with multiple stoke projects:
myworkspace/
├── frontend/         # python
│   └── stoke.toml
├── backend/          # java
│   └── stoke.toml
└── engine/           # cpp
└── stoke.toml

Run in the root:

```bash
stoke ide-sync
```

Generates:

- `.vscode/settings.json` — workspace-level settings
- `myworkspace.code-workspace` — multi-root VSCode workspace

Open the `.code-workspace` file to work on all projects together.

See [`stoke ide-sync`](../commands/ide-sync.md) for details.

## Regenerating IDE files

IDE files are regenerated on every `stoke build`. If they get out of sync (e.g. after changing dependencies), just rebuild:

```bash
stoke build
```

Or force it:

```bash
stoke build --force
```

## Not modifying manually

Since IDE files are regenerated, manual edits are overwritten on the next build. Configure via `stoke.toml` instead.

Add extra include paths in `stoke.toml`:

```toml
[targets.myapp]
include_dirs = ["third_party/include"]
```

## Related

- [`stoke ide-sync`](../commands/ide-sync.md)
- [`stoke build`](../commands/build.md)