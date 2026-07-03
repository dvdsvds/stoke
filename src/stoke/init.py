import sys
from pathlib import Path

from stoke.python_versions import detect_all, PythonInstall


def _prompt(question: str, default: str | None = None) -> str:
    """텍스트 입력 받기. 빈 입력이면 default 반환."""
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "

    answer = input(prompt).strip()
    if not answer and default is not None:
        return default
    return answer


def _prompt_choice(question: str, choices: list[str], default_index: int = 0) -> int:
    """번호로 선택 받기. 1-indexed로 보여주고 0-indexed로 반환."""
    print(f"\n{question}")
    for i, choice in enumerate(choices, start=1):
        marker = " (default)" if (i - 1) == default_index else ""
        print(f"  {i}. {choice}{marker}")

    while True:
        answer = input(f"Select [1-{len(choices)}, default {default_index + 1}]: ").strip()
        if not answer:
            return default_index

        if not answer.isdigit():
            print(f"  Please enter a number between 1 and {len(choices)}")
            continue

        num = int(answer)
        if 1 <= num <= len(choices):
            return num - 1
        print(f"  Please enter a number between 1 and {len(choices)}")


def _prompt_yes_no(question: str, default: bool = True) -> bool:
    """예/아니오 입력."""
    default_str = "Y/n" if default else "y/N"
    while True:
        answer = input(f"{question} [{default_str}]: ").strip().lower()
        if not answer:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please answer 'y' or 'n'")


def _select_python_version(installs: list[PythonInstall]) -> str:
    """감지된 파이썬 중 하나 선택. 선택된 버전의 'major.minor' 문자열 반환."""
    if not installs:
        print("Error: No Python installations detected on this system", file=sys.stderr)
        sys.exit(1)

    # 표시용 문자열: "Python 3.14.0 (C:\...\python.exe)"
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

    # major.minor만 반환 (예: "3.14")
    full_version = installs[selected_index].version
    parts = full_version.split(".")
    return ".".join(parts[:2])


def _select_lock_mode() -> str:
    """lock 파일 위치 선택."""
    choices = [
        "commit  - Lock file at project root (stoke.lock), commit to git for team reproducibility",
        "local   - Lock file inside .stoke/ (gitignored), each developer has their own",
    ]
    selected = _prompt_choice(
        "Lock file mode:",
        choices,
        default_index=0,
    )
    return "commit" if selected == 0 else "local"


def _write_stoke_toml(
    path: Path,
    project_name: str,
    python_version: str,
    lock_mode: str,
) -> None:
    """stoke.toml 파일 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "python"
python_version = "{python_version}"
sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.{project_name}.deps]
'''
    path.write_text(content, encoding="utf-8")


def cmd_init() -> None:
    """대화형 프로젝트 초기화."""
    cwd = Path.cwd()
    stoke_toml_path = cwd / "stoke.toml"

    # 이미 있으면 덮어쓸지 확인
    if stoke_toml_path.exists():
        print(f"stoke.toml already exists at {stoke_toml_path}")
        if not _prompt_yes_no("Overwrite?", default=False):
            print("Aborted.")
            return

    print("\n=== stoke project setup ===\n")

    # 1. 프로젝트 이름
    default_name = cwd.name
    project_name = _prompt("Project name", default=default_name)

    # 프로젝트 이름 검증: 파이썬 식별자 규칙 (간단 버전)
    if not project_name.replace("_", "").replace("-", "").isalnum():
        print(
            f"Error: project name '{project_name}' contains invalid characters",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. 파이썬 버전 선택
    installs = detect_all()
    python_version = _select_python_version(installs)

    # 3. lock 모드 선택
    lock_mode = _select_lock_mode()

    # 4. 최종 확인
    print("\n=== Summary ===")
    print(f"  Project name:   {project_name}")
    print(f"  Python version: {python_version}")
    print(f"  Lock mode:      {lock_mode}")
    print(f"  Config file:    {stoke_toml_path}")

    if not _prompt_yes_no("\nCreate stoke.toml?", default=True):
        print("Aborted.")
        return

    # 5. stoke.toml 생성
    _write_stoke_toml(stoke_toml_path, project_name, python_version, lock_mode)
    print(f"\nCreated {stoke_toml_path}")
    print("Next: run 'stoke build' to build your project.")