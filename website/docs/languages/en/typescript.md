# TypeScript

stoke supports TypeScript projects using tsx runtime (no compilation step).

## Requirements

- Node.js 18 or higher
- Install via `stoke install --language=nodejs --version=<version>`

## Configuration

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "typescript"
entry = "src/main.ts"
```

## How it works

- `stoke build` runs `npm install`
- `stoke run` executes the entry with `tsx` (compile + run in one step)
- Dependencies via `package.json`
- Type checking via `tsconfig.json`

## Example

```bash
mkdir myapp
cd myapp
stoke init
```

Select `TypeScript`. stoke creates:

- `stoke.toml`
- `package.json` with `tsx`, `typescript`, `@types/node`
- `tsconfig.json`
- `src/main.ts` with hello-world

Then:

```bash
stoke build
stoke run
```

## Framework scaffolding

```bash
stoke init nextjs       # Next.js — React full-stack
stoke init nestjs       # NestJS — Angular-style backend
stoke init vite         # Vite — fast frontend build tool
stoke init nuxt         # Nuxt — Vue full-stack
stoke init sveltekit    # SvelteKit — Svelte full-stack
stoke init hono         # Hono — edge computing framework
```

See [Frameworks](../frameworks/en/overview.md) for details.

## Notes

- Uses `tsx` for runtime (no separate compilation step)
- For production builds, use each framework's build command (e.g. `npm run build`)