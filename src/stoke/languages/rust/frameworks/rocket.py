"""Rocket (Rust) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt, resolve_project_dir
from stoke.tool_install import ensure_cargo

def cmd_init_rocket():
    """stoke init rocket 명령어."""
    print("Creating Rocket (Rust) project\n")

    project_name, project_path, is_empty = resolve_project_dir("myapp")

    _write_stoke_toml(project_path, project_name)
    (project_path / "src").mkdir(exist_ok=True)
    _write_cargo_toml(project_path / "Cargo.toml", project_name)
    _write_main_rs(project_path / "src" / "main.rs")

    cargo = ensure_cargo(project_path)
    if cargo:
        cargo_exe, cargo_env = cargo
        print("\nFetching dependencies (cargo check)...")
        result = subprocess.run(
            [cargo_exe, "check"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            env=cargo_env,
        )
        if result.returncode != 0:
            print("\nWarning: cargo check failed:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
    else:
        print("\nWarning: 'cargo' not found. Install Rust from https://rustup.rs", file=sys.stderr)

    print(f"\nRocket project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print("After running, open: http://localhost:8000/")

def _write_stoke_toml(project_path: Path, project_name: str) -> None:
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "commit"

[targets.{project_name}]
language = "rust"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_cargo_toml(path: Path, project_name: str) -> None:
    content = f'''[package]
name = "{project_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
rocket = "0.5"
'''
    path.write_text(content, encoding="utf-8")

def _write_main_rs(path: Path) -> None:
    content = '''#[macro_use] extern crate rocket;

#[get("/")]
fn home() -> &'static str {
    "Hello from Rocket + stoke!"
}

#[get("/hello/<name>")]
fn hello(name: &str) -> String {
    format!("Hello, {}!", name)
}

#[launch]
fn rocket() -> _ {
    rocket::build().mount("/", routes![home, hello])
}
'''
    path.write_text(content, encoding="utf-8")
