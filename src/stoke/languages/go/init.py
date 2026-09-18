"""Go 프로젝트 초기화 로직."""
import subprocess
import shutil
import sys
from pathlib import Path
import re

from stoke.prompts import _prompt, _prompt_yes_no, sanitize_go_module_name
from stoke.tool_install import ensure_tool

def _select_go_version() -> str:
    """선택적 Go 버전 pin (빈 입력이면 pin 안 함)."""
    return _prompt("Pin Go version? (e.g. 1.22.3, blank to skip)", default="").strip()

def _select_go_module_name(project_name: str) -> str:
    """published될 프로젝트만 실제 모듈 경로를 물어봄. 아니면 project_name을 그대로 씀."""
    if not _prompt_yes_no("Will this be published (e.g. on GitHub)?", default=False):
        return project_name
    return sanitize_go_module_name(
        _prompt("Go module name (e.g. github.com/user/myapp)", project_name), project_name
    )

def _pin_go_version(project_root: Path, version: str) -> None:
    """go.mod의 go/toolchain 지시문을 patch (빈 문자열이면 아무것도 안 함)."""
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

def _write_example_go(project_root: Path, project_name: str, module_name: str | None = None) -> None:
    """Go 예시 파일 생성 + go.mod 초기화."""
    module_name = module_name or project_name
    go_exe = ensure_tool("go", ("go", "go.exe"), project_root, display_name="Go")
    if go_exe:
        result = subprocess.run(
            [go_exe, "mod", "init", module_name],
            cwd=str(project_root),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Warning: go mod init failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    else:
        print(f"Warning: 'go' not found. Run manually: go mod init {module_name}", file=sys.stderr)
    main_go = project_root / "main.go"
    content = '''package main

import "fmt"

func main() {
    fmt.Println("Hello from stoke!")
}
'''
    main_go.write_text(content, encoding="utf-8")