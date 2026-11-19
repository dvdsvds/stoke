"""stoke env -- 프로젝트 로컬 툴체인을 현재 셸 PATH에 올리는 스크립트 출력 (`stoke exec` 접두어 없이 쓰고 싶을 때).

stoke는 부모 셸의 환경을 직접 바꿀 수 없으므로 셸에 적용할 스크립트를 stdout에 내보내고, 사용자가 적용:

    bash/zsh:    eval "$(stoke env)"
    PowerShell:  stoke env | Out-String | Invoke-Expression

그 뒤에는 `go mod tidy`, `cargo add`처럼 접두어 없이 실행 가능. PATH에 올릴 경로는 `stoke exec`과 같은
계산(tool_install.toolchain_env)을 그대로 써서 두 명령이 항상 같은 결과를 냄.
다시 실행하면 이전에 stoke env가 넣은 항목은 빼고 새로 구성하므로 중복되지 않고, 프로젝트를 옮겨도
이전 프로젝트 경로가 남지 않음. 되돌리기는 `stoke env --off`.
"""
import os
import re
import sys
from pathlib import Path

from stoke.config import find_config_file
from stoke.tool_install import toolchain_env

# toolchain_env가 프로젝트 로컬 경로를 얹어주는 언어들 (exec과 동일한 범위)
_LANGUAGES = ("go", "rust", "javascript", "csharp", "ruby", "php")

def collect(project_root: Path) -> tuple[list[str], dict[str, str], list[str]]:
    """(PATH 앞에 올릴 폴더들, 추가 환경변수, 로컬 툴체인이 있는 언어들)."""
    base_path = os.environ.get("PATH", "")
    path_dirs: list[str] = []
    env_vars: dict[str, str] = {}
    languages: list[str] = []

    for language in _LANGUAGES:
        env = toolchain_env(language, project_root)
        full_path = env.get("PATH", "")
        # toolchain_env는 기존 PATH 앞에 폴더를 붙이므로, 붙은 앞부분만 잘라냄
        if full_path != base_path and full_path.endswith(base_path):
            languages.append(language)
            for entry in full_path[:len(full_path) - len(base_path)].split(os.pathsep):
                if entry and entry not in path_dirs:
                    path_dirs.append(entry)
        for name, value in env.items():
            if name != "PATH" and os.environ.get(name) != value:
                env_vars[name] = value
                if language not in languages:
                    languages.append(language)
    return path_dirs, env_vars, languages

def _quote(shell_kind: str, value: str) -> str:
    if shell_kind == "powershell":
        # PowerShell은 곡선 따옴표도 따옴표로 취급하므로 전부 두 번씩
        return "'" + re.sub("(['‘’‚‛])", r"\1\1", value) + "'"
    return "'" + value.replace("'", "'\\''") + "'"

def _split_env_list(name: str, sep: str) -> list[str]:
    return [x for x in os.environ.get(name, "").split(sep) if x]

def build_script(shell_kind: str, path_dirs: list[str], env: dict[str, str]) -> str:
    """셸에 적용할 스크립트 문자열. path_dirs/env가 비어 있으면 이전 stoke env 흔적만 제거."""
    sep = os.pathsep

    # 이전에 stoke env가 넣은 항목은 빼고, 그 위에 새 항목을 앞에 붙임 (중복·이전 프로젝트 잔여 방지)
    old_dirs = set(_split_env_list("STOKE_ENV_PATHS", sep))
    kept = [p for p in os.environ.get("PATH", "").split(sep) if p and p not in old_dirs and p not in path_dirs]
    full_path = sep.join(path_dirs + kept)
    stale_vars = [v for v in _split_env_list("STOKE_ENV_VARS", ",") if v not in env]

    q = lambda v: _quote(shell_kind, v)
    lines: list[str] = []
    if shell_kind == "powershell":
        lines.append(f"$env:PATH = {q(full_path)}")
        for name, value in env.items():
            lines.append(f"$env:{name} = {q(value)}")
        for name in stale_vars:
            lines.append(f"Remove-Item Env:{name} -ErrorAction SilentlyContinue")
        lines.append(f"$env:STOKE_ENV_PATHS = {q(sep.join(path_dirs))}" if path_dirs
                     else "Remove-Item Env:STOKE_ENV_PATHS -ErrorAction SilentlyContinue")
        lines.append(f"$env:STOKE_ENV_VARS = {q(','.join(env))}" if env
                     else "Remove-Item Env:STOKE_ENV_VARS -ErrorAction SilentlyContinue")
    else:
        lines.append(f"export PATH={q(full_path)}")
        for name, value in env.items():
            lines.append(f"export {name}={q(value)}")
        for name in stale_vars:
            lines.append(f"unset {name}")
        lines.append(f"export STOKE_ENV_PATHS={q(sep.join(path_dirs))}" if path_dirs else "unset STOKE_ENV_PATHS")
        lines.append(f"export STOKE_ENV_VARS={q(','.join(env))}" if env else "unset STOKE_ENV_VARS")
    return "\n".join(lines) + "\n"

def cmd_env(shell: str | None, off: bool) -> None:
    """stoke env [--shell=bash|zsh|sh|powershell] [--off]"""
    if shell is None:
        shell = "powershell" if sys.platform == "win32" else "bash"
    shell_kind = "powershell" if shell in ("powershell", "pwsh") else "posix"

    if shell_kind == "posix" and sys.platform == "win32":
        print("Error: bash/zsh on Windows isn't supported by 'stoke env' yet - use PowerShell.", file=sys.stderr)
        sys.exit(1)

    try:
        project_root = find_config_file().parent
    except FileNotFoundError:
        print("Error: stoke.toml not found in this directory or any parent.", file=sys.stderr)
        print("Run 'stoke env' from inside a project created with 'stoke init'.", file=sys.stderr)
        sys.exit(1)

    if off:
        path_dirs, env_vars, languages = [], {}, []
    else:
        path_dirs, env_vars, languages = collect(project_root)

    sys.stdout.write(build_script(shell_kind, path_dirs, env_vars))

    if off:
        print("stoke env: removed project toolchains from this shell", file=sys.stderr)
    elif languages:
        print(f"stoke env: {', '.join(languages)}", file=sys.stderr)
    else:
        print(f"stoke env: no project-local toolchains in {project_root / '.stoke' / 'toolchains'}", file=sys.stderr)
        print("  Install one with: stoke install <language>", file=sys.stderr)

    if sys.stdout.isatty():
        apply = ("stoke env | Out-String | Invoke-Expression" if shell_kind == "powershell"
                 else 'eval "$(stoke env)"')
        if off:
            apply = apply.replace("stoke env", "stoke env --off")
        print(f"  This only printed the script. Apply it to your shell with:  {apply}", file=sys.stderr)
