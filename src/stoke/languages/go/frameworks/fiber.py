"""Fiber (Go) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt

def cmd_init_fiber():
    """stoke init fiber 명령어."""
    print("Creating Fiber (Go) project\n")

    cwd = Path.cwd()
    is_empty = not any(cwd.iterdir())

    if is_empty:
        default_name = cwd.name
        project_name = _prompt("Project name", default_name)
        project_path = cwd
    else:
        project_name = _prompt("Project name", "myapp")
        project_path = cwd / project_name
        if project_path.exists():
            print(f"Error: directory '{project_name}' already exists", file=sys.stderr)
            sys.exit(1)
        project_path.mkdir()

    module_name = _prompt("Go module name (e.g. github.com/user/myapp)", project_name)

    (project_path / "handlers").mkdir()

    _write_stoke_toml(project_path, project_name)
    _write_main_go(project_path / "main.go", module_name)
    _write_handlers_hello(project_path / "handlers" / "hello.go")

    go_exe = shutil.which("go")
    if go_exe:
        print(f"\nInitializing go.mod (module: {module_name})...")
        subprocess.run(
            [go_exe, "mod", "init", module_name],
            cwd=str(project_path),
            capture_output=True,
        )
        print("Downloading Fiber dependency...")
        subprocess.run(
            [go_exe, "get", "github.com/gofiber/fiber/v2"],
            cwd=str(project_path),
            capture_output=True,
        )
    else:
        print("\nWarning: 'go' not found.", file=sys.stderr)

    print(f"\nFiber project created at: {project_path}")
    print()
    print("Next steps:")
    print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print("After running, open: http://localhost:3000/")

def _write_stoke_toml(project_path: Path, project_name: str) -> None:
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "commit"

[targets.{project_name}]
language = "go"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_main_go(path: Path, module_name: str) -> None:
    content = f'''package main

import (
    "log"

    "github.com/gofiber/fiber/v2"

    "{module_name}/handlers"
)

func main() {{
    app := fiber.New()

    app.Get("/", handlers.Home)
    app.Get("/hello/:name", handlers.Hello)

    log.Println("Server starting on :3000")
    if err := app.Listen(":3000"); err != nil {{
        log.Fatal(err)
    }}
}}
'''
    path.write_text(content, encoding="utf-8")

def _write_handlers_hello(path: Path) -> None:
    content = '''package handlers

import (
    "github.com/gofiber/fiber/v2"
)

func Home(c *fiber.Ctx) error {
    return c.JSON(fiber.Map{
        "message": "Hello from Fiber + stoke!",
    })
}

func Hello(c *fiber.Ctx) error {
    name := c.Params("name")
    return c.JSON(fiber.Map{
        "message": "Hello, " + name + "!",
    })
}
'''
    path.write_text(content, encoding="utf-8")