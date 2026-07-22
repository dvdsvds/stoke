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
- `uvicorn[standard]` (latest)

> **Note**: On Python 3.13+ with venv, `uvicorn[standard]` may fail to install due to `watchfiles` requiring Rust. Use conda environment as a workaround.

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