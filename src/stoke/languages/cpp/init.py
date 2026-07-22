"""C++ 프로젝트 초기화 로직."""
from pathlib import Path

from stoke.prompts import _prompt_choice

def _select_cpp_standard() -> str:
    """C++ 표준 선택."""
    choices = ["c++17", "c++20", "c++23", "c++14", "c++11"]
    standards = ["c++17", "c++20", "c++23", "c++14", "c++11"]
    selected = _prompt_choice(
        "C++ standard:",
        choices,
        default_index=0,
    )
    return standards[selected]

def _write_stoke_toml_cpp(
    path: Path,
    project_name: str,
    cpp_standard: str,
    lock_mode: str,
) -> None:
    """C++ 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "cpp"
cpp_standard = "{cpp_standard}"
sources = ["src/**/*.cpp"]
'''
    path.write_text(content, encoding="utf-8")

def _write_example_cpp(project_root: Path) -> None:
    """C++ 예시 파일 생성."""
    src_dir = project_root / "src"
    src_dir.mkdir(exist_ok=True)
    main_path = src_dir / "main.cpp"
    if not main_path.exists():
        main_path.write_text(
            '#include <iostream>\n'
            '\n'
            'int main() {\n'
            '    std::cout << "Hello from stoke!" << std::endl;\n'
            '    return 0;\n'
            '}\n',
            encoding="utf-8",
        )