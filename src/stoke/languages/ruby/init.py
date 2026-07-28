"""Ruby 프로젝트 초기화 로직."""
from pathlib import Path

from stoke.prompts import _prompt

def _select_ruby_version() -> str:
    """
    선택적 Ruby 버전 pin.
    빈 입력이면 pin 안 함 (팀원마다 로컬 ruby 버전이 달라도 됨).
    """
    return _prompt(
        "Pin Ruby version? (e.g. 3.3.0, blank to skip)", default=""
    ).strip()

def _write_ruby_version_file(project_root: Path, version: str) -> None:
    """
    .ruby-version 생성. rbenv/rvm/asdf/chruby가 이 파일을 자동으로 읽어서
    지정된 버전을 사용하도록 강제함.
    version이 빈 문자열이면 아무것도 안 함.
    """
    if not version:
        return
    (project_root / ".ruby-version").write_text(version + "\n", encoding="utf-8")

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
