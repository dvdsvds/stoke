"""Go 프로젝트 초기화 로직."""
import subprocess
import shutil
import sys
from pathlib import Path
import re

from stoke.prompts import _prompt

def _select_go_version() -> str:
    """
    선택적 Go 버전 pin.
    빈 입력이면 pin 안 함 (go.mod가 로컬 go 버전을 그대로 씀).
    """
    return _prompt("Pin Go version? (e.g. 1.22.3, blank to skip)", default="").strip()

def _pin_go_version(project_root: Path, version: str) -> None:
    """
    go.mod의 go/toolchain 지시문을 patch. Go 툴체인이 자동으로 읽어서
    버전이 낮으면 빌드를 실패시키거나(go) 알아서 다운로드함(toolchain).
    version이 빈 문자열이면 아무것도 안 함.
    """
    if not version:
        return
    go_mod = project_root / "go.mod"
    if not go_mod.is_file():
        return
    text = go_mod.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^go .+$", f"go {version}", text, count=1)
    if re.search(r"(?m)^toolchain ", text):
        text = re.sub(r"(?m)^toolchain .+$", f"toolchain go{version}", text, count=1)
    else:
        text = text.rstrip("\n") + f"\ntoolchain go{version}\n"
    go_mod.write_text(text, encoding="utf-8")

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
        result = subprocess.run(
            [go_exe, "mod", "init", project_name],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Warning: go mod init failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    main_go = project_root / "main.go"
    content = '''package main

import "fmt"

func main() {
    fmt.Println("Hello from stoke!")
}
'''
    main_go.write_text(content, encoding="utf-8")