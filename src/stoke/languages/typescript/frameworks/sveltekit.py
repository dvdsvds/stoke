"""SvelteKit 프로젝트 스캐폴딩 (npm create svelte 사용)."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt


def cmd_init_sveltekit():
    """stoke init sveltekit 명령어."""
    print("Creating SvelteKit project via npm create svelte\n")

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

    npx_exe = shutil.which("npx")
    if npx_exe is None:
        print("Error: npx not found in PATH.", file=sys.stderr)
        sys.exit(1)

    print(f"\nRunning: npx sv create {project_name}\n")

    try:
        if is_empty:
            result = subprocess.run(
                [npx_exe, "sv", "create", "."],
                cwd=str(cwd),
                shell=True,
            )
            project_path = cwd
        else:
            result = subprocess.run(
                [npx_exe, "sv", "create", project_name],
                cwd=str(cwd),
                shell=True,
            )
            project_path = cwd / project_name
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)

    if result.returncode != 0:
        print("Error: sveltekit creation failed", file=sys.stderr)
        sys.exit(1)

    print(f"\nSvelteKit project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  npm install")
    print(f"  npm run dev")
    print()
    print("After running, open: http://localhost:5173/")