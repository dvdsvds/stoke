# Fastify

Create a Fastify project via:

```bash
stoke init fastify
```

Fastify is a fast, low-overhead web framework for Node.js.

## Prompts

- **Project name**: directory name for the project

## Generated files

    myapp/
    ├── stoke.toml
    ├── package.json
    └── src/
        ├── main.js                # Fastify entry point
        └── routes/
            └── hello.js           # sample router

## Dependencies

- `fastify` (^5.0.0)

## Default settings

- **Port**: `3000`
- **Host**: `0.0.0.0`
- **Logger**: enabled
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Fastify + stoke!"}`
  - `GET /hello/:name` → `{"message": "Hello, {name}!"}`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:3000/`

## Notes

- Uses ES modules (`"type": "module"` in package.json)
- Fastify is generally faster than Express and includes built-in JSON schema validation

## Customization

- Change port: edit `port: 3000` in `src/main.js`
- Add routes: create files in `src/routes/` and register in `main.js`
- Add plugins: use `fastify.register(...)` in `main.js`