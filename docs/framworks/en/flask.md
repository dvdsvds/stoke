# Flask

Create a Flask project via:

```bash
stoke init flask
```

## Prompts

- **Project name**: directory name for the project
- **Python version**: selected from detected installations (same as `stoke init`)
- **Environment type**: venv or conda

## Generated files

    myapp/
    ├── stoke.toml
    └── src/
        ├── main.py                        # Flask entry point
        └── app/
            ├── __init__.py                # create_app()
            ├── routes.py                  # register_routes()
            ├── templates/
            │   └── index.html             # Jinja2 template
            └── static/
                └── style.css              # sample stylesheet

## Dependencies

- `flask` (latest)

## Default settings

- **Host**: `0.0.0.0`
- **Port**: `5000`
- **Debug mode**: on
- **Endpoints**:
  - `GET /` → HTML page (rendered from `templates/index.html`)
  - `GET /api/hello/<name>` → `{"message": "Hello, {name}!"}`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:5000/`

## Customization

- Change port: edit `port=5000` in `src/main.py`
- Add routes: edit `src/app/routes.py`
- Add templates: create `.html` files in `src/app/templates/`
- Add static files: place CSS/JS/images in `src/app/static/`