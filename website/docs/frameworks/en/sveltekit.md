# SvelteKit

Create a SvelteKit project via:

```bash
stoke init sveltekit
```

SvelteKit is a Svelte full-stack framework with SSR, SSG, and file-based routing.

## Prompts

stoke calls `npx sv create` which prompts:

- **Template**: SvelteKit minimal, demo app, or library
- **TypeScript?**
- **Additional tools**: ESLint, Prettier, Playwright, Vitest

## Generated files

Standard SvelteKit structure:

    myapp/
    ├── src/
    │   ├── routes/
    │   └── app.html
    ├── static/
    ├── svelte.config.js
    ├── vite.config.ts
    └── package.json

## Dependencies

Standard SvelteKit dependencies.

## Run

Not managed by stoke — use SvelteKit commands directly:

```bash
cd myapp
npm install
npm run dev         # Development server
npm run build       # Production build
npm run preview     # Preview production build
```

Open `http://localhost:5173/`

## Notes

- stoke does not build or run SvelteKit projects
- SvelteKit compiles Svelte components at build time
- Refer to the [SvelteKit documentation](https://svelte.dev/docs/kit) for details