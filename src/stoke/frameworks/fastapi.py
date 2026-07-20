"""FastAPI 프로젝트 스캐폴딩."""
import sys
from pathlib import Path


def cmd_init_fastapi():
    """stoke init fastapi 명령어."""
    print("Creating FastAPI project\n")

    # 사용자 입력
    project_name = _prompt("Project name", "myapp")
    python_version = _prompt("Python version", "3.12")
    env_type_choice = _prompt("Environment type [venv/conda]", "venv")
    env_type = "conda" if env_type_choice.strip().lower() == "conda" else "venv"

    project_path = Path.cwd() / project_name
    if project_path.exists():
        print(f"Error: directory '{project_name}' already exists", file=sys.stderr)
        sys.exit(1)

    project_path.mkdir()

    # 폴더 구조 만들기
    (project_path / "src").mkdir()
    (project_path / "src" / "app").mkdir()
    (project_path / "src" / "app" / "routers").mkdir()

    # 파일 생성
    _write_stoke_toml(project_path, project_name, python_version, env_type)
    _write_main(project_path / "src" / "main.py", project_name)
    _write_app_init(project_path / "src" / "app" / "__init__.py")
    _write_routers_init(project_path / "src" / "app" / "routers" / "__init__.py")
    _write_hello_router(project_path / "src" / "app" / "routers" / "hello.py")

    print(f"\nFastAPI project created at: {project_path}")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print(f"After running, open: http://localhost:8000/")


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
fastapi = "*"
"uvicorn[standard]" = "*"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")


def _write_main(path: Path, project_name: str) -> None:
    content = '''import uvicorn
from app import create_app

app = create_app()


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
'''
    path.write_text(content, encoding="utf-8")


def _write_app_init(path: Path) -> None:
    content = '''from fastapi import FastAPI
from app.routers import hello


def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI + stoke")
    app.include_router(hello.router)
    return app
'''
    path.write_text(content, encoding="utf-8")


def _write_routers_init(path: Path) -> None:
    path.write_text("", encoding="utf-8")


def _write_hello_router(path: Path) -> None:
    content = '''from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "Hello from FastAPI + stoke!"}


@router.get("/hello/{name}")
def hello_name(name: str):
    return {"message": f"Hello, {name}!"}
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