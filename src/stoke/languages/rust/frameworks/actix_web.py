"""Actix-web (Rust) 프로젝트 스캐폴딩"""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt, resolve_project_dir

def cmd_init_actix_web():
    """stoke init actix-web 명령어"""
    print("Creating Actix-web (Rust) project\n")

    project_name, project_path, is_empty = resolve_project_dir("myapp")

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

    print(f"\nActix-web project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
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
actix-web = "4"
'''
    path.write_text(content, encoding="utf-8")

def _write_main_rs(path: Path) -> None:
    content = '''use actix_web::{get, web, App, HttpServer, Responder};

#[get("/")]
async fn home() -> impl Responder {
    "Hello from Actix-web + stoke!"
}

#[get("/hello/{name}")]
async fn hello(name: web::Path<String>) -> impl Responder {
    format!("Hello, {}!", name)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("Server starting on :8080");
    HttpServer::new(|| App::new().service(home).service(hello))
        .bind(("127.0.0.1", 8080))?
        .run()
        .await
}
'''
    path.write_text(content, encoding="utf-8")