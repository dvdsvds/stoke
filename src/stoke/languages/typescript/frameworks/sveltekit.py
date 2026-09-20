"""SvelteKit 프로젝트 스캐폴딩 (npm create svelte 사용)."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import resolve_project_name
from stoke.npm_check import warn_npm_health

def cmd_init_sveltekit():
    """stoke init sveltekit 명령어."""
    print("Creating SvelteKit project via npm create svelte\n")

    project_name, is_empty = resolve_project_name("myapp")
    cwd = Path.cwd()

    npm_exe = shutil.which("npm")
    if npm_exe is None:
        print("Error: npm not found in PATH.", file=sys.stderr)
        print("Install Node.js first.", file=sys.stderr)
        sys.exit(1)

    npx_exe = shutil.which("npx")
    if npx_exe is None:
        print("Error: npx not found in PATH.", file=sys.stderr)
        sys.exit(1)

    warn_npm_health(npm_exe)
    print(f"\nRunning: npx sv create {project_name}\n")

    try:
        if is_empty:
            result = subprocess.run(
                [npx_exe, "sv", "create", "."],
                cwd=str(cwd),
            )
            project_path = cwd
        else:
            result = subprocess.run(
                [npx_exe, "sv", "create", project_name],
                cwd=str(cwd),
            )
            project_path = cwd / project_name
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)

    if result.returncode != 0:
        print("Error: sveltekit creation failed", file=sys.stderr)
        sys.exit(1)

    _write_stoke_toml(project_path, project_name)

    print(f"\nSvelteKit project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print("After running, open: http://localhost:5173/")

def _write_stoke_toml(project_path: Path, project_name: str) -> None:
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "commit"

[targets.{project_name}]
language = "typescript"
run_script = "dev"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")