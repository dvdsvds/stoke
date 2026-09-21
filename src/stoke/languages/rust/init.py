"""Rust 프로젝트 초기화 로직"""
import subprocess
import shutil
import sys
from pathlib import Path

from stoke.prompts import _prompt, _prompt_choice
from stoke.languages.rust.versions import RustInstall
from stoke.tool_install import ensure_cargo

def _select_rust_version(installs: list[RustInstall]) -> str:
    """감지된 Rust 툴체인 중 하나 선택 (또는 직접 입력/생략). 반환값은 rust-toolchain.toml의 channel로 씀."""
    choices = ["Don't pin - use whatever toolchain is active"]
    for install in installs:
        default_mark = " (installed default)" if install.is_default else ""
        label = install.channel
        if install.exact_version != install.channel:
            label += f" ({install.exact_version})"
        choices.append(f"{label}{default_mark}")
    choices.append("Enter manually")

    selected = _prompt_choice("Pin Rust toolchain version?", choices, default_index=0)
    if selected == 0:
        return ""
    if selected == len(choices) - 1:
        return _prompt("Rust toolchain version (e.g. 1.75.0)", default="").strip()
    return installs[selected - 1].channel

def _write_rust_toolchain(project_root: Path, version: str) -> None:
    """rust-toolchain.toml 생성 (rustup이 자동으로 읽어서 버전 강제)."""
    if not version:
        return
    content = f'''[toolchain]
channel = "{version}"
'''
    (project_root / "rust-toolchain.toml").write_text(content, encoding="utf-8")

def _write_stoke_toml_rust(
    path: Path,
    project_name: str,
    lock_mode: str,
) -> None:
    """Rust 프로젝트용 stoke.toml 쓰기"""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "rust"
'''
    path.write_text(content, encoding="utf-8")

def _write_example_rust(project_root: Path, project_name: str) -> None:
    """Rust 예시 파일 생성 + Cargo.toml 초기화"""
    cargo = ensure_cargo(project_root)
    if cargo:
        cargo_exe, cargo_env = cargo
        result = subprocess.run(
            [cargo_exe, "init", "--name", project_name, "--vcs", "none"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            env=cargo_env,
        )
        if result.returncode != 0:
            print("Warning: cargo init failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    else:
        cargo_toml = project_root / "Cargo.toml"
        cargo_toml.write_text(
            f'''[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
''',
            encoding="utf-8",
        )
        (project_root / "src").mkdir(exist_ok=True)

    main_rs = project_root / "src" / "main.rs"
    main_rs.parent.mkdir(parents=True, exist_ok=True)
    content = '''fn main() {
    println!("Hello from stoke!");
}
'''
    main_rs.write_text(content, encoding="utf-8")

