"""stoke exec — 프로젝트 로컬 툴체인을 PATH(및 필요 시 환경변수)에 얹어서 임의 명령 실행.

`stoke install`/`stoke init`이 언어를 `.stoke/toolchains/`에 프로젝트 전용으로
설치해도 시스템 PATH는 건드리지 않는다 (의도된 격리). `stoke build`/`run`은
어댑터가 내부적으로 그 경로를 직접 호출해서 잘 동작하지만, 사용자가 직접
셸에서 치는 네이티브 도구 명령(`go mod tidy`, `cargo add`, `bundle add`,
`composer require`, `dotnet add package` 등)은 시스템 PATH만 보다가
"명령을 찾을 수 없음"으로 실패한다. `stoke exec -- <command>`는 현재 타겟
언어의 프로젝트 로컬 툴체인 bin을 PATH 맨 앞에 얹은 환경에서 그 명령을
그대로 실행해서 이 갭을 메운다.

각 언어의 실행파일/환경변수 탐색은 해당 어댑터가 이미 하는 것과 동일한
로직(`tool_install.py`의 `_find_toolchain_dir`/`_find_toolchain_exe`, Rust는
`ensure_cargo`와 동일하게 RUSTUP_HOME/CARGO_HOME도 같이 설정, Node.js는
`_node_tools.find_local_node_dir`)을 재사용한다.
"""
import os
import subprocess
import sys
from pathlib import Path

from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit
from stoke.languages._node_tools import find_local_node_dir
from stoke.tool_install import _find_toolchain_dir, _find_toolchain_exe

_EXE_NAME = {
    "go": "go.exe" if sys.platform == "win32" else "go",
    "csharp": "dotnet.exe" if sys.platform == "win32" else "dotnet",
    "ruby": "ruby.exe" if sys.platform == "win32" else "ruby",
    "php": "php.exe" if sys.platform == "win32" else "php",
}

def _toolchain_env(language: str, project_root: Path) -> dict:
    """language의 프로젝트 로컬 툴체인 bin을 PATH 맨 앞에 얹은 환경변수.
    못 찾으면 os.environ 그대로 반환 (시스템 PATH만 보는 기존 동작과 동일)."""
    env = dict(os.environ)

    if language == "rust":
        toolchain_dir = _find_toolchain_dir(project_root, "rust")
        if toolchain_dir is not None:
            exe_name = "cargo.exe" if sys.platform == "win32" else "cargo"
            cargo_bin = toolchain_dir / "cargo" / "bin"
            if (cargo_bin / exe_name).is_file():
                env["RUSTUP_HOME"] = str(toolchain_dir / "rustup")
                env["CARGO_HOME"] = str(toolchain_dir / "cargo")
                env["PATH"] = str(cargo_bin) + os.pathsep + env.get("PATH", "")
        return env

    if language in ("javascript", "typescript"):
        local_dir = find_local_node_dir(project_root)
        if local_dir is not None:
            bin_dir = local_dir if sys.platform == "win32" else local_dir / "bin"
            if bin_dir.is_dir():
                env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
        return env

    exe_name = _EXE_NAME.get(language)
    if exe_name is not None:
        exe_path = _find_toolchain_exe(project_root, language, exe_name)
        if exe_path is not None:
            env["PATH"] = str(exe_path.parent) + os.pathsep + env.get("PATH", "")
    return env

def cmd_exec(command: list[str], target_name: str | None) -> None:
    """stoke exec [--target=X] -- <command...>"""
    command = [arg for arg in command if arg != "--"]
    if not command:
        print("Error: 'stoke exec' needs a command to run, e.g. 'stoke exec -- go mod tidy'", file=sys.stderr)
        sys.exit(1)

    config = load_config_or_exit()
    target_name = resolve_target_or_exit(config, target_name, verb="running in")
    target = config.targets[target_name]
    project_root = config.config_path.parent

    env = _toolchain_env(target.language, project_root)

    try:
        result = subprocess.run(command, cwd=str(project_root), env=env)
    except FileNotFoundError:
        print(f"Error: '{command[0]}' not found (checked project-local {target.language} toolchain and PATH).", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)

    sys.exit(result.returncode)
