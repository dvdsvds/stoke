# Nuxt

Create a Nuxt project via:

```bash
stoke init nuxt
```

Nuxt is a Vue.js full-stack framework with SSR, SSG, and file-based routing.

## Prompts

stoke calls `nuxi init` which prompts:

- **Template**: minimal or other templates
- **Package manager**: npm / yarn / pnpm / bun
- **Initialize git repository?**

## Generated files

Standard Nuxt structure:

    myapp/
    ├── app.vue
    ├── nuxt.config.ts
    ├── package.json
    └── (pages/, components/, etc.)

## Dependencies

Standard Nuxt dependencies (nuxt, vue).

## Run

Not managed by stoke — use Nuxt commands directly:

```bash
cd myapp
npm install
npm run dev         # Development server
npm run build       # Production build
npm run preview     # Preview production build
```

Open `http://localhost:3000/`

## Notes

- stoke does not build or run Nuxt projects
- Nuxt uses file-based routing similar to Next.js but for Vue
- Refer to the [Nuxt documentation](https://nuxt.com/docs) for details