"""Rust 프로젝트 초기화 로직"""
import subprocess
import shutil
from pathlib import Path

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