# Python

stoke handles Python projects with venv creation, dependency installation, and syntax checking.

## Example `stoke.toml`

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "python"
python_version = "3.12"
entry = "src/main.py"
sources = ["src/**/*.py"]

[targets.myapp.deps]
requests = "*"
flask = ">=2.0"
```

## Target fields

| Field | Required | Description |
|-------|----------|-------------|
| `language` | Yes | Must be `"python"` |
| `python_version` | No | Required Python version (e.g. `"3.12"`) |
| `entry` | Yes | Entry script path for `stoke run` |
| `sources` | No | Glob patterns for syntax checking |
| `deps` | No | pip dependencies |

## Python version detection

Set `python_version` to require a specific version:

```toml
python_version = "3.12"        # requires 3.12.x
python_version = "3.12.5"      # requires exactly 3.12.5
```

stoke searches for a matching Python in:

1. `PATH` (`python3.12`, `python3`, `python`)
2. `py` launcher (Windows)
3. Common installation paths (`%LOCALAPPDATA%\Programs\Python\...`, `/usr/bin/python3.X`, etc.)

If no matching Python is found, stoke exits with an error listing all detected Pythons.

Check what's available:

```bash
stoke python list
```

## venv

stoke creates a project-local venv at:
.stoke/python/{target}/venv/

The venv is Python version–specific. If you change `python_version`, stoke recreates it.

## Dependencies

Declare pip dependencies in `[targets.<name>.deps]`:

```toml
[targets.myapp.deps]
requests = "*"                 # any version
flask = ">=2.0"                # version constraint
numpy = "==1.24.3"             # exact version
mypackage = "git+https://..."  # VCS
```

On `stoke build`, stoke:

1. Reads installed packages in the venv
2. Compares with declared deps and lock file
3. Installs/updates as needed
4. Writes locked versions to `.stoke/lock.toml`

Subsequent builds skip installation if the venv already matches the lock file.

## Source layout

stoke uses standard Python conventions. Structure your project so imports work from the project root:
myapp/
├── stoke.toml
└── src/
├── main.py
├── utils/
│   ├── init.py
│   └── helpers.py
└── models/
├── init.py
└── user.py

In `main.py`:

```python
from utils.helpers import greet
from models.user import User
```

Use full paths from `src/`. Each subfolder needs `__init__.py`.

stoke sets `PYTHONPATH` appropriately when running.

## Syntax checking

`stoke build` also runs `py_compile` on all files matching `sources`:
Building 'myapp' (python)...
Using Python 3.12.12
Checked 3 file(s), all passed
Build complete: myapp

Errors are reported per file:
FAIL  src\main.py
SyntaxError: unexpected EOF while parsing

## Running

```bash
stoke run
```

Runs `entry` with the venv's Python and the correct `PYTHONPATH`.

## IDE integration

stoke generates `.vscode/settings.json` with:

- Python interpreter set to the venv
- Extra paths for imports
- File exclusions (`.stoke/`, `__pycache__/`)

## Related

- [`stoke build`](../commands/build.md)
- [`stoke run`](../commands/run.md)
- [Lock file](../configuration/lock-file.md)