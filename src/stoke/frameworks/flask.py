"""Flask 프로젝트 스캐폴딩."""
import sys
from pathlib import Path


def cmd_init_flask():
    """stoke init flask 명령어."""
    print("Creating Flask project\n")

    project_name = _prompt("Project name", "myapp")
    python_version = _prompt("Python version", "3.12")
    env_type_choice = _prompt("Environment type [venv/conda]", "venv")
    env_type = "conda" if env_type_choice.strip().lower() == "conda" else "venv"

    project_path = Path.cwd() / project_name
    if project_path.exists():
        print(f"Error: directory '{project_name}' already exists", file=sys.stderr)
        sys.exit(1)

    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src" / "app").mkdir()

    _write_stoke_toml(project_path, project_name, python_version, env_type)
    _write_main(project_path / "src" / "main.py")
    _write_app_init(project_path / "src" / "app" / "__init__.py")
    _write_routes(project_path / "src" / "app" / "routes.py")

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
    content = '''from flask import Flask, jsonify


def register_routes(app: Flask) -> None:
    @app.route("/")
    def home():
        return jsonify({"message": "Hello from Flask + stoke!"})

    @app.route("/hello/<name>")
    def hello(name: str):
        return jsonify({"message": f"Hello, {name}!"})
'''
    path.write_text(content, encoding="utf-8")


def _prompt(question: str, default: str | None = None) -> str:
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "
    while True:
        try:
            value = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)
        if value:
            return value
        if default is not None:
            return default
        print("Value required.")