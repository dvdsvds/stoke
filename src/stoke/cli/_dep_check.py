"""stoke audit/outdated 공용 헬퍼 -- 둘 다 "언어별로 네이티브 도구에 위임, --json이면 구조화하거나
원본을 감싸서 반환" 구조가 거의 동일해서 공유. audit.py/outdated.py 둘만 씀 (public API 아님)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

from stoke.tool_install import run_with_toolchain_or_hint, toolchain_env

def emit_raw_json(language: str, returncode: int, stdout: str) -> None:
    """dotnet/go/rust/ruby -- 구조화 안 하고 원본 출력을 감싸서 반환 (--json이지만 반쪽짜리임을 명시)."""
    print(json.dumps({
        "language": language,
        "structured": False,
        "note": "stoke doesn't parse this tool's own output yet -- see 'raw_output'",
        "exit_code": returncode,
        "raw_output": stdout,
    }, indent=2))

def json_wrapped_external(
    language: str, exe_names, display_name: str, install_hint: str, cmd_builder, project_root: Path, json_output: bool,
) -> int:
    """govulncheck/cargo-audit(outdated)/bundler-audit(outdated)처럼 별도 설치 필요한 외부 도구 공용 실행."""
    if not json_output:
        return run_with_toolchain_or_hint(language, exe_names, display_name, cmd_builder, install_hint, project_root)

    env = toolchain_env(language, project_root)
    exe_name = exe_names[1] if sys.platform == "win32" and isinstance(exe_names, tuple) else (exe_names[0] if isinstance(exe_names, tuple) else exe_names)
    exe = shutil.which(exe_name, path=env.get("PATH")) or shutil.which(exe_name)
    if exe is None:
        print(json.dumps({
            "language": language, "structured": False,
            "error": f"{display_name} not found. Install it with: {install_hint}",
        }, indent=2))
        return 1

    result = subprocess.run(cmd_builder(exe), cwd=str(project_root), env=env, capture_output=True, text=True, errors="replace")
    emit_raw_json(language, result.returncode, result.stdout + result.stderr)
    return result.returncode

def find_dotnet(project_root: Path) -> tuple[str | None, dict]:
    """dotnet 실행 파일 경로 (프로젝트 로컬 우선) + 그 PATH가 반영된 env."""
    env = toolchain_env("csharp", project_root)
    dotnet_exe = shutil.which("dotnet", path=env.get("PATH")) or shutil.which("dotnet")
    return dotnet_exe, env

def find_csproj(project_root: Path, target_name: str) -> Path | None:
    """<target_name>/ 서브디렉토리 우선, 없으면 프로젝트 루트에서 *.csproj 찾기."""
    subdir_csproj = list((project_root / target_name).glob("*.csproj"))
    root_csproj = list(project_root.glob("*.csproj"))
    matches = subdir_csproj or root_csproj
    return matches[0] if matches else None
