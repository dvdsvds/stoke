"""stoke exec — 프로젝트 로컬 툴체인(.stoke/toolchains)을 PATH에 얹어서 임의 명령 실행."""
import subprocess
import sys

from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit
from stoke.tool_install import toolchain_env as _toolchain_env

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
