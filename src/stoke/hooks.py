"""pre_build/post_build 훅 실행."""
import subprocess
from pathlib import Path

def run_hooks(commands: list[str], project_root: Path, label: str) -> None:
    """pre_build/post_build 커맨드를 순서대로 실행 (하나라도 실패하면 즉시 RuntimeError)."""
    for cmd in commands:
        print(f"[{label}] {cmd}")
        result = subprocess.run(
            cmd, shell=True, cwd=str(project_root), capture_output=True, text=True, errors="replace",
        )
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.returncode != 0:
            if result.stderr:
                print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")
            raise RuntimeError(f"{label} hook failed (exit {result.returncode}): {cmd}")
