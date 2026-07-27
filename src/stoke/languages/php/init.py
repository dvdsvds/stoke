"""PHP 프로젝트 초기화 로직."""
from pathlib import Path

def _write_stoke_toml_php(
    path: Path,
    project_name: str,
    lock_mode: str,
) -> None:
    """PHP 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "php"
entry = "src/main.php"
'''
    path.write_text(content, encoding="utf-8")

def _write_example_php(project_root: Path) -> None:
    """PHP 예시 파일 생성."""
    src = project_root / "src"
    src.mkdir(exist_ok=True)
    main_php = src / "main.php"
    if main_php.exists():
        return

    content = '<?php\n\necho "Hello from stoke!\\n";\n'
    main_php.write_text(content, encoding="utf-8")
