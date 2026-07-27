"""Ruby 프로젝트 초기화 로직."""
from pathlib import Path

def _write_stoke_toml_ruby(
    path: Path,
    project_name: str,
    lock_mode: str,
) -> None:
    """Ruby 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "ruby"
entry = "src/main.rb"
'''
    path.write_text(content, encoding="utf-8")

def _write_example_ruby(project_root: Path) -> None:
    """Ruby 예시 파일 생성."""
    src = project_root / "src"
    src.mkdir(exist_ok=True)
    main_rb = src / "main.rb"
    if main_rb.exists():
        return

    content = 'puts "Hello from stoke!"\n'
    main_rb.write_text(content, encoding="utf-8")
