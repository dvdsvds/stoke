# FastAPI

Create a FastAPI project via:

```bash
stoke init fastapi
```

## Prompts

- **Project name**: directory name for the project
- **Python version**: selected from detected installations (same as `stoke init`)
- **Environment type**: venv or conda

## Generated files

    myapp/
    ├── stoke.toml
    └── src/
        ├── main.py                        # uvicorn entry point
        └── app/
            ├── __init__.py                # create_app()
            └── routers/
                ├── __init__.py
                └── hello.py               # sample router

## Dependencies

- `fastapi` (latest)
- `uvicorn` (latest)

> **Note**: The template uses plain `uvicorn` (not `uvicorn[standard]`) to avoid the Rust-based `watchfiles` build on Python 3.13+. If you need auto-reload or performance extras, add `uvicorn[standard]` to `stoke.toml` manually (conda environment recommended for that case).

## Default settings

- **Host**: `0.0.0.0`
- **Port**: `8000`
- **Endpoints**:
  - `GET /` → `{"message": "Hello from FastAPI + stoke!"}`
  - `GET /hello/{name}` → `{"message": "Hello, {name}!"}`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8000/`

## Customization

- Change port: edit `port=8000` in `src/main.py`
- Add routers: create files in `src/app/routers/` and register them in `src/app/__init__.py`