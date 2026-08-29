# Express

Create an Express project via:

```bash
stoke init express
```

Express is a classic, minimal web framework for Node.js.

## Prompts

- **Project name**: directory name for the project

## Generated files

    myapp/
    ├── stoke.toml
    ├── package.json
    └── src/
        ├── main.js                # Express entry point
        └── routes/
            └── hello.js           # sample router

## Dependencies

- `express` (^4.19.0)

## Default settings

- **Port**: `3000`
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Express + stoke!"}`
  - `GET /hello/:name` → `{"message": "Hello, {name}!"}`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:3000/`

## Customization

- Change port: edit `PORT` in `src/main.js`
- Add routes: create files in `src/routes/` and register in `main.js`
- Add middleware: use `app.use(...)` in `main.js`