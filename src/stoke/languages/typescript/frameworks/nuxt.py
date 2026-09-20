"""Nuxt 프로젝트 스캐폴딩 (nuxi 사용)."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import resolve_project_name
from stoke.npm_check import warn_npm_health
from stoke.languages._node_tools import write_dev_server_stoke_toml

def cmd_init_nuxt():
    """stoke init nuxt 명령어."""
    print("Creating Nuxt project via nuxi\n")

    cwd = Path.cwd()
    project_name, is_empty = resolve_project_name("myapp")

    npx_exe = shutil.which("npx")
    if npx_exe is None:
        print("Error: npx not found in PATH.", file=sys.stderr)
        print("Install Node.js first.", file=sys.stderr)
        sys.exit(1)

    npm_exe = shutil.which("npm")
    if npm_exe:
        warn_npm_health(npm_exe)

    print(f"\nRunning: npx nuxi@latest init {project_name}\n")

    try:
        if is_empty:
            result = subprocess.run(
                [npx_exe, "nuxi@latest", "init", "."],
                cwd=str(cwd),
            )
            project_path = cwd
        else:
            result = subprocess.run(
                [npx_exe, "nuxi@latest", "init", project_name],
                cwd=str(cwd),
            )
            project_path = cwd / project_name
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)

    if result.returncode != 0:
        print("Error: nuxi init failed", file=sys.stderr)
        sys.exit(1)

    write_dev_server_stoke_toml(project_path, project_name)

    print(f"\nNuxt project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print("After running, open: http://localhost:3000/")