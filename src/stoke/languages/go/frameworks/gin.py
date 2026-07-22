"""Gin (Go) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt

def cmd_init_gin():
    """stoke init gin 명령어."""
    print("Creating Gin (Go) project\n")

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
        print("Downloading Gin dependency...")
        subprocess.run(
            [go_exe, "get", "github.com/gin-gonic/gin"],
            cwd=str(project_path),
            capture_output=True,
        )
    else:
        print("\nWarning: 'go' not found. Run these manually:", file=sys.stderr)
        print(f"  cd {project_name}", file=sys.stderr)
        print(f"  go mod init {module_name}", file=sys.stderr)
        print(f"  go get github.com/gin-gonic/gin", file=sys.stderr)

    print(f"\nGin project created at: {project_path}")
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
language = "go"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_main_go(path: Path, module_name: str) -> None:
    content = f'''package main

import (
    "log"

    "github.com/gin-gonic/gin"

    "{module_name}/handlers"
)

func main() {{
    r := gin.Default()

    r.GET("/", handlers.Home)
    r.GET("/hello/:name", handlers.Hello)

    log.Println("Server starting on :8080")
    if err := r.Run(":8080"); err != nil {{
        log.Fatal(err)
    }}
}}
'''
    path.write_text(content, encoding="utf-8")

def _write_handlers_hello(path: Path) -> None:
    content = '''package handlers

import (
    "net/http"

    "github.com/gin-gonic/gin"
)

func Home(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{
        "message": "Hello from Gin + stoke!",
    })
}

func Hello(c *gin.Context) {
    name := c.Param("name")
    c.JSON(http.StatusOK, gin.H{
        "message": "Hello, " + name + "!",
    })
}
'''
    path.write_text(content, encoding="utf-8")