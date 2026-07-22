"""Express (Node.js) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
import json
from pathlib import Path

from stoke.prompts import _prompt

def cmd_init_express():
    """stoke init express 명령어."""
    print("Creating Express project\n")

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

    # npm install
    npm_exe = shutil.which("npm")
    if npm_exe:
        print("\nRunning npm install...")
        subprocess.run(
            [npm_exe, "install"],
            cwd=str(project_path),
            capture_output=True,
            shell=True,
        )
    else:
        print("\nWarning: npm not found. Install manually.", file=sys.stderr)

    print(f"\nExpress project created at: {project_path}")
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
        "scripts": {
            "start": "node src/main.js"
        },
        "dependencies": {
            "express": "^4.19.0"
        }
    }
    (project_path / "package.json").write_text(
        json.dumps(pkg, indent=2), encoding="utf-8"
    )

def _write_main(path: Path) -> None:
    content = '''const express = require("express");
const helloRouter = require("./routes/hello");

const app = express();
const PORT = 3000;

app.use(express.json());

app.get("/", (req, res) => {
    res.json({ message: "Hello from Express + stoke!" });
});

app.use("/hello", helloRouter);

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
'''
    path.write_text(content, encoding="utf-8")

def _write_hello_route(path: Path) -> None:
    content = '''const express = require("express");
const router = express.Router();

router.get("/:name", (req, res) => {
    const name = req.params.name;
    res.json({ message: `Hello, ${name}!` });
});

module.exports = router;
'''
    path.write_text(content, encoding="utf-8")