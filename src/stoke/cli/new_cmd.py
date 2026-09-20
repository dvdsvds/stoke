"""stoke new -- 서브디렉토리를 만들고 그 안에 새 프로젝트를 초기화 (모노레포에 서비스 추가용)."""
import os
import sys
from pathlib import Path

from stoke.config import load_config
from stoke.init import cmd_init_noninteractive
from stoke.prompts import _VALID_PROJECT_NAME, _sanitize_project_name
from stoke.toml_editor import add_workspace_member

def cmd_new(
    name: str,
    language: str | None,
    version: str | None,
    env_type: str | None,
    lock_mode: str,
    vcpkg: bool,
) -> None:
    """stoke new <name> -l <language> [-V <version>] -- ./<name>/ 밑에 독립된 stoke.toml 생성."""
    if language is None:
        print("Error: 'stoke new' needs a language, e.g. 'stoke new backend -l python'", file=sys.stderr)
        sys.exit(1)

    # name이 그대로 서브디렉토리 이름이 되니까, 디렉토리 만들기 전에 먼저 검증 --
    # '/'나 '..'가 들어있으면 상위 디렉토리 밖에 디렉토리가 생길 수 있음.
    if not _VALID_PROJECT_NAME.match(name):
        suggestion = _sanitize_project_name(name)
        print(
            f"Error: '{name}' isn't a valid service name (letters/digits/-/_ only, must start with a letter).\n"
            f"  Try: stoke new {suggestion} -l {language}" + (f" -V {version}" if version else ""),
            file=sys.stderr,
        )
        sys.exit(1)

    parent = Path.cwd()
    target_dir = parent / name
    if target_dir.exists():
        print(f"Error: '{target_dir}' already exists", file=sys.stderr)
        sys.exit(1)

    target_dir.mkdir(parents=True)
    try:
        os.chdir(target_dir)
        cmd_init_noninteractive(
            language=language,
            project_name=name,
            version=version,
            env_type=env_type,
            lock_mode=lock_mode,
            vcpkg=vcpkg,
            yes=False,
        )
    finally:
        os.chdir(parent)

    parent_toml = parent / "stoke.toml"
    if not parent_toml.exists():
        return

    try:
        parent_config = load_config(parent_toml)
    except (FileNotFoundError, ValueError):
        return

    if parent_config.workspace is not None:
        add_workspace_member(parent_toml, name)
        print(f"Added '{name}' to workspace members in {parent_toml}")
