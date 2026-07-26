"""Next.js 프로젝트 스캐폴딩 (create-next-app 사용)."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import resolve_project_name

def cmd_init_nextjs():
    """stoke init nextjs 명령어."""
    print("Creating Next.js project via create-next-app\n")

    project_name, is_empty = resolve_project_name("myapp") 
    cwd = Path.cwd()

    npx_exe = shutil.which("npx")
    if npx_exe is None:
        print("Error: npx not found in PATH.", file=sys.stderr)
        print("Install Node.js first.", file=sys.stderr)
        sys.exit(1)

    print(f"\nRunning: npx create-next-app@latest\n")

    try:
        if is_empty:
            result = subprocess.run(
                [npx_exe, "create-next-app@latest", "."],
                cwd=str(cwd),
                shell=True,
            )
            project_path = cwd
        else:
            result = subprocess.run(
                [npx_exe, "create-next-app@latest", project_name],
                cwd=str(cwd),
                shell=True,
            )
            project_path = cwd / project_name
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)

    if result.returncode != 0:
        print("Error: create-next-app failed", file=sys.stderr)
        sys.exit(1)

    print(f"\nNext.js project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  npm run dev")
    print()
    print("After running, open: http://localhost:3000/")