"""Rust 프로젝트 초기화 로직"""
import re
import subprocess
import shutil
import tomllib
from pathlib import Path

from stoke.prompts import _prompt

def _select_rust_version() -> str:
    """
    선택적 Rust 툴체인 버전 pin.
    빈 입력이면 pin 안 함 (팀원마다 로컬 rustc 버전이 달라도 됨).
    """
    return _prompt(
        "Pin Rust toolchain version? (e.g. 1.75.0, blank to skip)", default=""
    ).strip()

def _write_rust_toolchain(project_root: Path, version: str) -> None:
    """
    rust-toolchain.toml 생성. rustup이 이 파일을 자동으로 읽어서
    프로젝트 안에서 cargo/rustc를 실행할 때 지정된 버전을 강제함.
    version이 빈 문자열이면 아무것도 안 함.
    """
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
    cargo_exe = shutil.which("cargo")
    if cargo_exe:
        subprocess.run(
            [cargo_exe, "init", "--name", project_name, "--vcs", "none"],
            cwd=str(project_root),
            capture_output=True,
        )
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

def _write_example_rust_subdir(target_root: Path, target_name: str) -> None:
    """
    멀티 타겟 프로젝트에 두 번째 이후 Rust 타겟 추가할 때 사용.
    target_root 안에 자체 Cargo.toml + src/main.rs를 갖춘 완전한 패키지를 생성함
    (Cargo 워크스페이스 멤버). 루트 Cargo.toml의 [workspace] members 등록은
    _add_rust_workspace_member()가 별도로 처리.
    """
    target_root.mkdir(parents=True, exist_ok=True)
    cargo_toml = target_root / "Cargo.toml"
    cargo_toml.write_text(
        f'''[package]
name = "{target_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
''',
        encoding="utf-8",
    )
    src_dir = target_root / "src"
    src_dir.mkdir(exist_ok=True)
    main_rs = src_dir / "main.rs"
    main_rs.write_text(
        f'''fn main() {{
    println!("Hello from stoke! ({target_name})");
}}
''',
        encoding="utf-8",
    )

def _add_rust_workspace_member(root_cargo_toml_path: Path, new_member: str) -> None:
    """
    루트 Cargo.toml에 Cargo 워크스페이스 멤버 추가.

    [workspace] 섹션이 이미 있으면 members 리스트에 추가, 없으면 새로 만듦.
    루트 Cargo.toml은 자체 [package]를 유지한 채로 [workspace]도 같이 가질 수
    있음 ("워크스페이스 루트 패키지") -- 그래서 첫 번째 Rust 타겟의 기존 파일은
    안 건드리고 [workspace] 섹션만 추가/갱신하면 됨.
    """
    if not root_cargo_toml_path.is_file():
        raise RuntimeError(
            f"{root_cargo_toml_path} not found -- expected an existing Rust project"
        )

    with open(root_cargo_toml_path, "rb") as f:
        data = tomllib.load(f)

    members = list(data.get("workspace", {}).get("members", []))
    if new_member in members:
        return
    members.append(new_member)
    members_toml = "[" + ", ".join(f'"{m}"' for m in members) + "]"

    text = root_cargo_toml_path.read_text(encoding="utf-8")
    if "[workspace]" in text:
        if re.search(r"(?m)^members\s*=", text):
            text = re.sub(r"(?m)^members\s*=.*$", f"members = {members_toml}", text, count=1)
        else:
            text = text.replace("[workspace]", f"[workspace]\nmembers = {members_toml}", 1)
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += f"\n[workspace]\nmembers = {members_toml}\n"

    root_cargo_toml_path.write_text(text, encoding="utf-8")