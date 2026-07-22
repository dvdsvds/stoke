"""Hono 프로젝트 스캐폴딩 (npm create hono 사용)."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt

def cmd_init_hono():
    """stoke init hono 명령어."""
    print("Creating Hono project via npm create hono\n")

    cwd = Path.cwd()
    is_empty = not any(cwd.iterdir())

    if is_empty:
        default_name = cwd.name
        project_name = _prompt("Project name", default_name)
    else:
        project_name = _prompt("Project name", "myapp")

    npm_exe = shutil.which("npm")
    if npm_exe is None:
        print("Error: npm not found in PATH.", file=sys.stderr)
        print("Install Node.js first.", file=sys.stderr)
        sys.exit(1)

    print(f"\nRunning: npm create hono@latest {project_name}\n")

    try:
        if is_empty:
            result = subprocess.run(
                [npm_exe, "create", "hono@latest", "."],
                cwd=str(cwd),
                shell=True,
            )
            project_path = cwd
        else:
            result = subprocess.run(
                [npm_exe, "create", "hono@latest", project_name],
                cwd=str(cwd),
                shell=True,
            )
            project_path = cwd / project_name
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)

    if result.returncode != 0:
        print("Error: hono creation failed", file=sys.stderr)
        sys.exit(1)

    print(f"\nHono project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  npm install")
    print(f"  npm run dev")