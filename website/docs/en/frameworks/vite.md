# Vite

Create a Vite project via:

```bash
stoke init vite
```

Vite is a fast frontend build tool. Supports React, Vue, Svelte, and vanilla JavaScript/TypeScript.

## Prompts

stoke calls `npm create vite@latest` which prompts:

- **Project name**
- **Framework**: React, Vue, Svelte, Solid, Preact, Lit, Qwik, Angular, vanilla
- **Variant**: JavaScript / TypeScript (and other options per framework)

## Generated files

Standard Vite project structure (varies by framework choice).

## Dependencies

Framework-specific dependencies plus Vite build tool.

## Run

Not managed by stoke — use Vite commands directly:

```bash
cd myapp
npm install
npm run dev         # Development server
npm run build       # Production build
npm run preview     # Preview production build
```

Open the URL shown by Vite (usually `http://localhost:5173/`)

## Notes

- stoke does not build or run Vite projects
- Vite provides hot module replacement (HMR) for fast development
- Refer to the [Vite documentation](https://vitejs.dev) for details