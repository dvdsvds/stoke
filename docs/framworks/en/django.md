# Django

Create a Django project via:

```bash
stoke init django
```

## Prompts

- **Project name**: directory name for the project (also used as Django project package)
- **Python version**: selected from detected installations (same as `stoke init`)
- **Environment type**: venv or conda

## Generated files

    myapp/
    ├── stoke.toml
    └── src/
        ├── main.py                        # stoke run entry (calls manage.py runserver)
        ├── manage.py                      # Django management CLI
        ├── myapp/                         # project package
        │   ├── __init__.py
        │   ├── settings.py                # Django settings
        │   ├── urls.py                    # root URL config
        │   ├── wsgi.py
        │   └── asgi.py
        ├── hello/                         # sample app
        │   ├── __init__.py
        │   ├── apps.py
        │   ├── views.py
        │   ├── urls.py
        │   └── templates/
        │       └── hello/
        │           └── index.html         # sample template
        └── static/
            └── style.css                  # sample stylesheet

## Dependencies

- `django` (latest)

## Default settings

- **Host**: `127.0.0.1`
- **Port**: `8000`
- **DEBUG**: `True`
- **Database**: SQLite (`db.sqlite3`)
- **Endpoints**:
  - `GET /` → HTML page (rendered from `hello/templates/hello/index.html`)
  - `GET /api/hello/<name>/` → `{"message": "Hello, {name}!"}`
  - `GET /admin/` → Django admin

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8000/`

## Notes

- `main.py` runs `manage.py runserver` via subprocess, so `stoke run` starts the development server
- 18 initial migrations are pending — run `python src/manage.py migrate` to apply
- For production, use a proper WSGI/ASGI server (gunicorn, uvicorn)

## Customization

- Change port: pass argument to `runserver` in `src/main.py`
- Add views: edit `src/hello/views.py` and register in `src/hello/urls.py`
- Add apps: create new folders under `src/`, register in `INSTALLED_APPS` in `settings.py`
- Add templates: create `.html` files in app's `templates/<appname>/`
- Add static files: place in `src/static/`