# NestJS

Create a NestJS project via:

```bash
stoke init nestjs
```

NestJS is a TypeScript backend framework with Angular-style architecture (modules, controllers, services).

## Prompts

- **Project name**
- **Package manager**: npm / yarn / pnpm (from NestJS CLI)

## Generated files

Standard NestJS structure:

    myapp/
    ├── src/
    │   ├── main.ts
    │   ├── app.module.ts
    │   ├── app.controller.ts
    │   └── app.service.ts
    ├── test/
    ├── package.json
    ├── tsconfig.json
    └── nest-cli.json

## Dependencies

Standard NestJS dependencies (@nestjs/common, @nestjs/core, rxjs, etc.).

## Run

Not managed by stoke — use NestJS commands directly:

```bash
cd myapp
npm run start:dev     # Development with hot-reload
npm run build         # Production build
npm run start:prod    # Production server
```

Open `http://localhost:3000/`

## Notes

- stoke does not build or run NestJS projects
- NestJS uses TypeScript compilation and its own CLI for scaffolding features
- Add modules: `nest g module <name>`
- Add controllers: `nest g controller <name>`
- Refer to the [NestJS documentation](https://docs.nestjs.com) for details