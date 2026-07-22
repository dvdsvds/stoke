"""C 프로젝트 초기화 로직."""
from pathlib import Path

from stoke.prompts import _prompt_choice, _prompt_yes_no

def _select_c_standard() -> str:
    """C 표준 선택."""
    choices = ["c17", "c11", "c99", "c89"]
    standards = ["c17", "c11", "c99", "c89"]
    selected = _prompt_choice(
        "C standard:",
        choices,
        default_index=0,
    )
    return standards[selected]

def _prompt_vcpkg_install() -> None:
    """
    C/C++ 프로젝트 생성 시 vcpkg 설치 여부 프롬프트.
    이미 설치돼있으면 스킵.
    사용자가 거절하면 그냥 진행 (deps 필요할 때 다시 안내).
    """
    from stoke.vcpkg import is_vcpkg_installed, install_vcpkg

    if is_vcpkg_installed():
        return

    print("\nvcpkg is not installed.")
    print("vcpkg is required for C/C++ dependency management.")
    if not _prompt_yes_no("Install vcpkg now?", default=True):
        print("Skipped. You can install later with 'stoke install vcpkg'.")
        return

    try:
        install_vcpkg()
    except RuntimeError as e:
        print(f"Warning: vcpkg installation failed: {e}")
        print("You can retry later with 'stoke install vcpkg'.")

def _write_stoke_toml_c(
    path: Path,
    project_name: str,
    c_standard: str,
    lock_mode: str,
) -> None:
    """C 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "c"
c_standard = "{c_standard}"
sources = ["src/**/*.c"]
'''
    path.write_text(content, encoding="utf-8")

def _write_example_c(project_root: Path) -> None:
    """C 예시 파일 생성."""
    src_dir = project_root / "src"
    src_dir.mkdir(exist_ok=True)
    main_path = src_dir / "main.c"
    if not main_path.exists():
        main_path.write_text(
            '#include <stdio.h>\n'
            '\n'
            'int main(void) {\n'
            '    printf("Hello from stoke!\\n");\n'
            '    return 0;\n'
            '}\n',
            encoding="utf-8",
        )