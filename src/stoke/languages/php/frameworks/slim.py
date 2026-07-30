"""Slim Framework (PHP) 프로젝트 스캐폴딩."""
import sys
import json
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import resolve_project_dir

def cmd_init_slim():
    """stoke init slim 명령어."""
    print("Creating Slim Framework (PHP) project\n")

    project_name, project_path, is_empty = resolve_project_dir("myapp")

    _write_stoke_toml(project_path, project_name)
    _write_composer_json(project_path / "composer.json", project_name)
    (project_path / "public").mkdir(exist_ok=True)
    _write_index_php(project_path / "public" / "index.php")

    composer_exe = shutil.which("composer")
    if composer_exe:
        print("Running composer install...")
        subprocess.run(
            [composer_exe, "install"],
            cwd=str(project_path),
            capture_output=True,
        )
    else:
        print("Warning: 'composer' not found. Install from https://getcomposer.org/download/", file=sys.stderr)

    print(f"\nSlim project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  composer install   (if not already run above)")
    print(f"  php -S localhost:8000 -t public")
    print()
    print("Note: Slim needs PHP's built-in dev server (command above), not 'stoke run' --")
    print("'stoke run' just executes public/index.php once and exits, it doesn't serve.")
    print("After starting the server, open: http://localhost:8000/")

def _write_stoke_toml(project_path: Path, project_name: str) -> None:
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "commit"

[targets.{project_name}]
language = "php"
entry = "public/index.php"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_composer_json(path: Path, project_name: str) -> None:
    data = {
        "name": f"stoke/{project_name}",
        "require": {
            "slim/slim": "^4.0",
            "slim/psr7": "^1.6",
        },
    }
    path.write_text(json.dumps(data, indent=4), encoding="utf-8")

def _write_index_php(path: Path) -> None:
    content = '''<?php

require __DIR__ . "/../vendor/autoload.php";

use Slim\\Factory\\AppFactory;

$app = AppFactory::create();

$app->get("/", function ($request, $response) {
    $response->getBody()->write("Hello from Slim + stoke!");
    return $response;
});

$app->get("/hello/{name}", function ($request, $response, $args) {
    $response->getBody()->write("Hello, " . $args["name"] . "!");
    return $response;
});

$app->run();
'''
    path.write_text(content, encoding="utf-8")
