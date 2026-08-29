# Next.js

Create a Next.js project via:

```bash
stoke init nextjs
```

Next.js is a React full-stack framework with SSR, SSG, and file-based routing.

## Prompts

stoke calls `create-next-app` which prompts:

- **Project name**
- **TypeScript?**
- **ESLint?**
- **Tailwind CSS?**
- **`src/` directory?**
- **App Router?**
- **Turbopack?**
- **Import alias?**

## Generated files

Standard Next.js structure (varies by options). Includes `package.json`, `next.config.ts`, `app/` or `pages/`, etc.

## Dependencies

Standard Next.js dependencies (Next.js, React, TypeScript if selected).

## Run

Not managed by stoke — use Next.js commands directly:

```bash
cd myapp
npm run dev         # Development server
npm run build       # Production build
npm start           # Production server
```

Open `http://localhost:3000/`

## Notes

- stoke does not build or run Next.js projects
- Next.js has its own build system optimized for React applications
- Refer to the [Next.js documentation](https://nextjs.org/docs) for details