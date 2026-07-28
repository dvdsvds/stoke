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

def _write_example_go_subdir(target_root: Path, target_name: str) -> None:
    """
    멀티 타겟 프로젝트에 두 번째 이후 Go 타겟 추가할 때 사용.
    go.mod는 프로젝트 루트에 이미 있다고 가정(첫 타겟에서 생성됨) —
    go.mod는 다시 안 만들고 <target_name>/main.go만 씀. Go는 module 하나
    밑에 여러 main 패키지(cmd/api, cmd/worker 등)를 두는 게 표준 관례라
    이렇게 해도 정상 빌드됨.
    """
    target_root.mkdir(parents=True, exist_ok=True)
    main_go = target_root / "main.go"
    content = f'''package main

import "fmt"

func main() {{
    fmt.Println("Hello from stoke! ({target_name})")
}}
'''
    main_go.write_text(content, encoding="utf-8")