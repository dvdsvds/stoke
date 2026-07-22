"""NestJS 프로젝트 스캐폴딩 (@nestjs/cli 사용)."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt

def cmd_init_nestjs():
    """stoke init nestjs 명령어."""
    print("Creating NestJS project via @nestjs/cli\n")

    cwd = Path.cwd()
    is_empty = not any(cwd.iterdir())

    if is_empty:
        default_name = cwd.name
        project_name = _prompt("Project name", default_name)
    else:
        project_name = _prompt("Project name", "myapp")

    npx_exe = shutil.which("npx")
    if npx_exe is None:
        print("Error: npx not found in PATH.", file=sys.stderr)
        print("Install Node.js first.", file=sys.stderr)
        sys.exit(1)

    print(f"\nRunning: npx @nestjs/cli new {project_name}\n")

    try:
        if is_empty:
            # 빈 폴더에서: --directory . 옵션
            result = subprocess.run(
                [npx_exe, "@nestjs/cli", "new", project_name, "--directory", ".", "--skip-git"],
                cwd=str(cwd),
                shell=True,
            )
            project_path = cwd
        else:
            result = subprocess.run(
                [npx_exe, "@nestjs/cli", "new", project_name, "--skip-git"],
                cwd=str(cwd),
                shell=True,
            )
            project_path = cwd / project_name
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)

    if result.returncode != 0:
        print("Error: nest new failed", file=sys.stderr)
        sys.exit(1)

    print(f"\nNestJS project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  npm run start:dev")
    print()
    print("After running, open: http://localhost:3000/")