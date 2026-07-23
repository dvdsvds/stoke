# JavaScript

stoke supports JavaScript projects using Node.js runtime.

## Requirements

- Node.js 18 or higher (recommended: latest LTS)
- Install via `stoke install --language=nodejs --version=<version>`

## Configuration

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "javascript"
entry = "src/main.js"
```

## How it works

- `stoke build` runs `npm install` (installs dependencies from `package.json`)
- `stoke run` executes `node <entry>`
- Dependencies are managed via `package.json`

## Example

Create a new JavaScript project:

```bash
mkdir myapp
cd myapp
stoke init
```

Select `JavaScript` from the language menu. stoke will:

- Create `stoke.toml`
- Create `package.json`
- Generate `src/main.js` with a hello-world example

Then:

```bash
stoke build
stoke run
```

## Framework scaffolding

```bash
stoke init express      # Express — classic Node.js web framework
stoke init fastify      # Fastify — fast, low-overhead framework
```

See [Frameworks](../frameworks/en/overview.md) for details.

## Notes

- stoke reads `entry` field from `stoke.toml` and runs it with Node.js
- `node_modules/` is automatically added to `.gitignore`
- Uses system Node.js (or the one added to PATH from `stoke install`)