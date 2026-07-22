"""Go 프로젝트 초기화 로직."""
import subprocess
import shutil
from pathlib import Path

def _write_stoke_toml_go(
    path: Path,
    project_name: str,
    lock_mode: str,
) -> None:
    """Go 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "go"
'''
    path.write_text(content, encoding="utf-8")

def _write_example_go(project_root: Path, project_name: str) -> None:
    """Go 예시 파일 생성 + go.mod 초기화."""
    go_exe = shutil.which("go")
    if go_exe:
        subprocess.run(
            [go_exe, "mod", "init", project_name],
            cwd=str(project_root),
            capture_output=True,
        )
    main_go = project_root / "main.go"
    content = '''package main

import "fmt"

func main() {
    fmt.Println("Hello from stoke!")
}
'''
    main_go.write_text(content, encoding="utf-8")