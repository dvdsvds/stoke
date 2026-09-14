"""pre_build/post_build 훅 실행."""
import subprocess
from pathlib import Path

def run_hooks(commands: list[str], project_root: Path, label: str) -> None:
    """
    stoke.toml의 pre_build/post_build 커맨드를 순서대로 실행.
    출력을 캡처해서 print()로 흘려보냄 -- stoke 자신의 진행 메시지와 순서가
    안 뒤섞이게 하기 위함 (다른 언어 어댑터들도 같은 이유로 subprocess 출력을 캡처함).
    하나라도 0이 아닌 종료 코드를 내면 즉시 중단하고 RuntimeError.
    """
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
