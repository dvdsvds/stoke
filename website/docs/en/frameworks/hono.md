# Hono

Create a Hono project via:

```bash
stoke init hono
```

Hono is a lightweight, ultrafast web framework for edge computing (Cloudflare Workers, Deno, Bun, Node.js).

## Prompts

stoke calls `npm create hono@latest` which prompts:

- **Project name**
- **Template**: Cloudflare Workers, Cloudflare Pages, Deno, Bun, Node.js, Vercel, AWS Lambda, and more
- **Package manager**

## Generated files

Structure varies by template (edge platform).

## Dependencies

Hono core plus platform-specific dependencies.

## Run

Not managed by stoke — use commands per platform:

```bash
cd myapp
npm install
npm run dev
```

The port and URL depend on the chosen platform (typically `http://localhost:8787/` for Cloudflare Workers).

## Notes

- stoke does not build or run Hono projects
- Hono is optimized for edge runtimes
- Compatible with Node.js, Deno, Bun, Cloudflare Workers, Vercel, AWS Lambda
- Refer to the [Hono documentation](https://hono.dev) for details