"""Python 프로젝트 초기화 로직."""
import sys
from pathlib import Path

from stoke.languages.python.versions import PythonInstall
from stoke.prompts import _prompt, _prompt_choice

def _select_python_version(installs: list[PythonInstall]) -> str:
    """감지된 파이썬 중 하나 선택. 선택된 버전의 'major.minor' 문자열 반환."""
    if not installs:
        print("Error: No Python installations detected on this system", file=sys.stderr)
        sys.exit(1)
    choices = []
    default_index = 0
    for i, install in enumerate(installs):
        default_mark = " (system default)" if install.is_default else ""
        choices.append(f"Python {install.version}{default_mark}")
        if install.is_default:
            default_index = i
    selected_index = _prompt_choice(
        "Select Python version:",
        choices,
        default_index=default_index,
    )
    full_version = installs[selected_index].version
    parts = full_version.split(".")
    return ".".join(parts[:2])

def _select_env_type() -> str:
    """venv 또는 conda 선택."""
    print()
    print("Python environment type:")
    print("  1. venv (default) - standard Python virtual environment")
    print("  2. conda - use conda environments (requires conda installed)")
    choice = _prompt("Select (1-2)", "1")
    if choice.strip() == "2":
        return "conda"
    return "venv"

def _write_stoke_toml_python(
    path: Path,
    project_name: str,
    python_version: str,
    lock_mode: str,
    env_type: str = "venv",
) -> None:
    """파이썬 프로젝트용 stoke.toml 쓰기."""
    env_type_line = f'env_type = "{env_type}"\n' if env_type != "venv" else ""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "python"
python_version = "{python_version}"
{env_type_line}sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.{project_name}.deps]
'''
    path.write_text(content, encoding="utf-8")

def _write_example_python(project_root: Path) -> None:
    """파이썬 예시 파일 생성."""
    src = project_root / "src"
    src.mkdir(exist_ok=True)
    main_py = src / "main.py"
    if main_py.exists():
        return
    content = '''def main():
    print("Hello from stoke!")


if __name__ == "__main__":
    main()
'''
    main_py.write_text(content, encoding="utf-8")