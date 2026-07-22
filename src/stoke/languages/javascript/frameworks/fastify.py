"""Fastify (Node.js) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
import json
from pathlib import Path

from stoke.prompts import _prompt

def cmd_init_fastify():
    """stoke init fastify 명령어."""
    print("Creating Fastify project\n")

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

    (project_path / "src").mkdir()
    (project_path / "src" / "routes").mkdir()

    _write_stoke_toml(project_path, project_name)
    _write_package_json(project_path, project_name)
    _write_main(project_path / "src" / "main.js")
    _write_hello_route(project_path / "src" / "routes" / "hello.js")

    npm_exe = shutil.which("npm")
    if npm_exe:
        print("\nRunning npm install...")
        subprocess.run(
            [npm_exe, "install"],
            cwd=str(project_path),
            capture_output=True,
            shell=True,
        )

    print(f"\nFastify project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
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
language = "javascript"
entry = "src/main.js"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_package_json(project_path: Path, project_name: str) -> None:
    pkg = {
        "name": project_name,
        "version": "1.0.0",
        "main": "src/main.js",
        "type": "module",
        "scripts": {
            "start": "node src/main.js"
        },
        "dependencies": {
            "fastify": "^5.0.0"
        }
    }
    (project_path / "package.json").write_text(
        json.dumps(pkg, indent=2), encoding="utf-8"
    )

def _write_main(path: Path) -> None:
    content = '''import Fastify from "fastify";
import helloRoute from "./routes/hello.js";

const fastify = Fastify({ logger: true });

fastify.get("/", async () => {
    return { message: "Hello from Fastify + stoke!" };
});

fastify.register(helloRoute, { prefix: "/hello" });

const start = async () => {
    try {
        await fastify.listen({ port: 3000, host: "0.0.0.0" });
    } catch (err) {
        fastify.log.error(err);
        process.exit(1);
    }
};

start();
'''
    path.write_text(content, encoding="utf-8")

def _write_hello_route(path: Path) -> None:
    content = '''export default async function helloRoute(fastify) {
    fastify.get("/:name", async (request) => {
        const name = request.params.name;
        return { message: `Hello, ${name}!` };
    });
}
'''
    path.write_text(content, encoding="utf-8")