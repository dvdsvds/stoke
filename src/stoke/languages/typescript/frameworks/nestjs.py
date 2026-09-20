"""NestJS 프로젝트 스캐폴딩 (@nestjs/cli 사용)."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import resolve_project_name
from stoke.npm_check import warn_npm_health

def cmd_init_nestjs():
    """stoke init nestjs 명령어."""
    print("Creating NestJS project via @nestjs/cli\n")

    project_name, is_empty = resolve_project_name("myapp")
    cwd = Path.cwd()

    npx_exe = shutil.which("npx")
    if npx_exe is None:
        print("Error: npx not found in PATH.", file=sys.stderr)
        print("Install Node.js first.", file=sys.stderr)
        sys.exit(1)

    npm_exe = shutil.which("npm")
    if npm_exe:
        warn_npm_health(npm_exe)

    print(f"\nRunning: npx @nestjs/cli new {project_name}\n")

    try:
        if is_empty:
            # 빈 폴더에서: --directory . 옵션
            result = subprocess.run(
                [npx_exe, "@nestjs/cli", "new", project_name, "--directory", ".", "--skip-git"],
                cwd=str(cwd),
            )
            project_path = cwd
        else:
            result = subprocess.run(
                [npx_exe, "@nestjs/cli", "new", project_name, "--skip-git"],
                cwd=str(cwd),
            )
            project_path = cwd / project_name
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)

    if result.returncode != 0:
        print("Error: nest new failed", file=sys.stderr)
        sys.exit(1)

    _write_stoke_toml(project_path, project_name)

    print(f"\nNestJS project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  stoke run")
    print()
    print("After running, open: http://localhost:3000/")

def _write_stoke_toml(project_path: Path, project_name: str) -> None:
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "commit"

[targets.{project_name}]
language = "typescript"
run_script = "start:dev"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")