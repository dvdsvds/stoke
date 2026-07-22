"""Flask 프로젝트 스캐폴딩."""
import sys
from pathlib import Path

from stoke.python_versions import detect_all
from stoke.init import _prompt, _select_python_version, _select_env_type

def cmd_init_flask():
    """stoke init flask 명령어."""
    print("Creating Flask project\n")

    cwd = Path.cwd()
    is_empty = not any(cwd.iterdir())

    if is_empty:
        default_name = cwd.name
        project_name = _prompt("Project name", default_name)
        project_path = cwd
    else:
        project_name = _prompt("Project name", "myapp")
        project_path = cwd / project_name
        if project_path.exists():
            print(f"Error: directory '{project_name}' already exists", file=sys.stderr)
            sys.exit(1)
        project_path.mkdir()

    installs = detect_all()
    python_version = _select_python_version(installs)
    env_type = _select_env_type()

    (project_path / "src").mkdir()
    (project_path / "src" / "app").mkdir()
    (project_path / "src" / "app" / "templates").mkdir()
    (project_path / "src" / "app" / "static").mkdir()

    _write_stoke_toml(project_path, project_name, python_version, env_type)
    _write_main(project_path / "src" / "main.py")
    _write_app_init(project_path / "src" / "app" / "__init__.py")
    _write_routes(project_path / "src" / "app" / "routes.py")
    _write_index_html(project_path / "src" / "app" / "templates" / "index.html")
    _write_style_css(project_path / "src" / "app" / "static" / "style.css")

    print(f"\nFlask project created at: {project_path}")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print(f"After running, open: http://localhost:5000/")

def _write_stoke_toml(project_path: Path, project_name: str, python_version: str, env_type: str) -> None:
    env_line = f'env_type = "{env_type}"\n' if env_type != "venv" else ""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "local"

[targets.{project_name}]
language = "python"
python_version = "{python_version}"
{env_line}sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.{project_name}.deps]
flask = "*"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_main(path: Path) -> None:
    content = '''from app import create_app

def main():
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()
'''
    path.write_text(content, encoding="utf-8")

def _write_app_init(path: Path) -> None:
    content = '''from flask import Flask

def create_app() -> Flask:
    app = Flask(__name__)
    from app.routes import register_routes
    register_routes(app)
    return app
'''
    path.write_text(content, encoding="utf-8")

def _write_routes(path: Path) -> None:
    content = '''from flask import Flask, jsonify, render_template

def register_routes(app: Flask) -> None:
    @app.route("/")
    def home():
        return render_template("index.html", title="Flask + stoke")

    @app.route("/api/hello/<name>")
    def api_hello(name: str):
        return jsonify({"message": f"Hello, {name}!"})
'''
    path.write_text(content, encoding="utf-8")

def _write_index_html(path: Path) -> None:
    content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>{{ title }}</h1>
    <p>Hello from Flask + stoke!</p>
    <p>Try: <a href="/api/hello/world">/api/hello/world</a></p>
</body>
</html>
'''
    path.write_text(content, encoding="utf-8")

def _write_style_css(path: Path) -> None:
    content = '''body {
    font-family: sans-serif;
    max-width: 720px;
    margin: 4rem auto;
    padding: 0 1rem;
    color: #333;
}

h1 {
    color: #0284c7;
}
'''
    path.write_text(content, encoding="utf-8")