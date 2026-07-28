"""PHP 프로젝트 초기화 로직."""
import json
from pathlib import Path

from stoke.prompts import _prompt

def _select_php_version() -> str:
    """
    선택적 PHP 버전 pin.
    빈 입력이면 pin 안 함 (팀원마다 로컬 php 버전이 달라도 됨).
    """
    return _prompt(
        "Pin PHP version constraint? (e.g. 8.2, blank to skip)", default=""
    ).strip()

def _write_composer_json_pin(project_root: Path, project_name: str, version: str) -> None:
    """
    composer.json을 php 버전 제약만 넣어서 생성.
    composer install이 실행되는 시점(Gemfile/composer.json 있는 프로젝트)에
    Composer 자체가 현재 PHP 버전을 이 제약과 비교해서 안 맞으면 에러를 냄.
    version이 빈 문자열이거나 이미 composer.json이 있으면 아무것도 안 함.

    주의: composer.json이 생기면 다음 'stoke build'부터 composer install이
    실행되므로, 이 프로젝트를 빌드하려면 Composer가 설치돼 있어야 함.
    """
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
    src.mkdir(exist_ok=True)
    main_php = src / "main.php"
    if main_php.exists():
        return

    content = '<?php\n\necho "Hello from stoke!\\n";\n'
    main_php.write_text(content, encoding="utf-8")
