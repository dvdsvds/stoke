"""Axum (Rust) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt, resolve_project_dir

def cmd_init_axum():
    """stoke init axum 명령어."""
    print("Creating Axum (Rust) project\n")

    project_name, project_path = resolve_project_dir("myapp")

    _write_stoke_toml(project_path, project_name)
    (project_path / "src").mkdir(exist_ok=True)
    _write_cargo_toml(project_path / "Cargo.toml", project_name)
    _write_main_rs(project_path / "src" / "main.rs")

    cargo_exe = shutil.which("cargo")
    if cargo_exe:
        print("\nFetching dependencies (cargo check)...")
        subprocess.run(
            [cargo_exe, "check"],
            cwd=str(project_path),
            capture_output=True,
        )
    else:
        print("\nWarning: 'cargo' not found. Install Rust from https://rustup.rs", file=sys.stderr)

    print(f"\nAxum project created at: {project_path}")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print("After running, open: http://localhost:8080/")

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
axum = "0.7"
tokio = {{ version = "1", features = ["full"] }}
'''
    path.write_text(content, encoding="utf-8")

def _write_main_rs(path: Path) -> None:
    content = '''use axum::{extract::Path, routing::get, Router};

async fn home() -> &'static str {
    "Hello from Axum + stoke!"
}

async fn hello(Path(name): Path<String>) -> String {
    format!("Hello, {}!", name)
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(home))
        .route("/hello/:name", get(hello));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:8080").await.unwrap();
    println!("Server starting on :8080");
    axum::serve(listener, app).await.unwrap();
}
'''
    path.write_text(content, encoding="utf-8")
