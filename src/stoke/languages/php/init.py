"""PHP 프로젝트 초기화 로직."""
import json
from pathlib import Path

from stoke.prompts import _prompt

def _select_php_version() -> str:
    """선택적 PHP 버전 pin (빈 입력이면 pin 안 함)."""
    return _prompt(
        "Pin PHP version constraint? (e.g. 8.2, blank to skip)", default=""
    ).strip()

def _write_composer_json_pin(project_root: Path, project_name: str, version: str) -> None:
    """composer.json을 php 버전 제약만 넣어서 생성 (생성되면 이후 build부터 composer install 필요)."""
    if not version:
        return
    composer_json = project_root / "composer.json"
    if composer_json.exists():
        return
    data = {
        "name": f"stoke/{project_name}",
        "require": {"php": f">={version}"},
    }
    composer_json.write_text(json.dumps(data, indent=4), encoding="utf-8")

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
    src.mkdir(parents=True, exist_ok=True)
    main_php = src / "main.php"
    if main_php.exists():
        return

    content = '<?php\n\necho "Hello from stoke!\\n";\n'
    main_php.write_text(content, encoding="utf-8")
