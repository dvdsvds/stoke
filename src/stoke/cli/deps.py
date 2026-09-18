"""stoke add/remove -- python/java는 stoke.toml이 매니페스트, JS/TS는 npm 우회 실행, 나머진 힌트만."""
import subprocess
import sys
from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit
from stoke.languages._node_tools import find_npm
from stoke.toml_editor import add_dep, remove_dep

_MANAGED_LANGUAGES = {"python", "java"}
_NPM_LANGUAGES = {"javascript", "typescript"}

_NATIVE_HINT = {
    "go": "go get <module>",
    "rust": "cargo add <crate>",
    "kotlin": "add it to build.gradle.kts under dependencies { }",
    "csharp": "dotnet add package <name>",
    "ruby": "bundle add <gem>",
    "php": "composer require <package>",
    "javascript": "npm install <package>",
    "typescript": "npm install <package>",
    "c": "stoke vcpkg install <library>",
    "cpp": "stoke vcpkg install <library>",
}

def _npm_add(config, specs: list[str]) -> None:
    """JS/TS: stoke.toml 대신 실제 npm install 실행 (npm 버그 우회, 여러 패키지 한 번에)."""
    from stoke.npm_check import resolve_npm_command

    try:
        npm_exe = find_npm(config.config_path.parent)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Running: npm install {' '.join(specs)}\n")
    result = subprocess.run(
        resolve_npm_command(npm_exe) + ["install", *specs],
        cwd=str(config.config_path.parent),
    )
    if result.returncode != 0:
        print(f"Error: npm install {' '.join(specs)} failed", file=sys.stderr)
        sys.exit(1)

def cmd_add_dep(packages: list[str], target_name: str | None):
    """stoke add <package> [package2 ...] [--target=X] (python/java는 패키지 하나 + 버전만)."""
    config = load_config_or_exit()
    target_name = resolve_target_or_exit(config, target_name, verb="adding to")
    target = config.targets[target_name]

    if target.language in _NPM_LANGUAGES:
        _npm_add(config, packages)
        return

    if target.language not in _MANAGED_LANGUAGES:
        hint = _NATIVE_HINT.get(target.language)
        print(f"Error: 'stoke add' doesn't apply to '{target.language}' targets.", file=sys.stderr)
        if hint:
            print(f"  stoke.toml isn't the dependency manifest here — use: {hint}", file=sys.stderr)
        sys.exit(1)

    if len(packages) > 2:
        print(f"Error: 'stoke add' takes one package (and an optional version) for '{target.language}' targets.", file=sys.stderr)
        sys.exit(1)

    package = packages[0]
    version = packages[1] if len(packages) == 2 else None

    if target.language == "java" and not version:
        print("Error: Java dependencies need an explicit version.", file=sys.stderr)
        print(f"  stoke add {package} <version> [--target={target_name}]", file=sys.stderr)
        sys.exit(1)

    resolved_version = version or "*"
    try:
        add_dep(config.config_path, target_name, package, resolved_version)
    except (OSError, ValueError) as e:
        print(f"Error updating stoke.toml: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Added to stoke.toml: {package} = \"{resolved_version}\" (target '{target_name}')\n")

    from stoke.cli.build import cmd_build
    cmd_build(target_name)

def _npm_remove(config, packages: list[str]) -> None:
    """javascript/typescript: stoke.toml 대신 실제 npm uninstall을 실행 (npm 버그 우회 포함)."""
    from stoke.npm_check import resolve_npm_command

    try:
        npm_exe = find_npm(config.config_path.parent)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Running: npm uninstall {' '.join(packages)}\n")
    result = subprocess.run(
        resolve_npm_command(npm_exe) + ["uninstall", *packages],
        cwd=str(config.config_path.parent),
    )
    if result.returncode != 0:
        print(f"Error: npm uninstall {' '.join(packages)} failed", file=sys.stderr)
        sys.exit(1)

def cmd_remove_dep(packages: list[str], target_name: str | None):
    """stoke remove <package> [package2 ...] [--target=X]"""
    config = load_config_or_exit()
    target_name = resolve_target_or_exit(config, target_name, verb="removing from")
    target = config.targets[target_name]

    if target.language in _NPM_LANGUAGES:
        _npm_remove(config, packages)
        return

    if target.language not in _MANAGED_LANGUAGES:
        hint = _NATIVE_HINT.get(target.language)
        print(f"Error: 'stoke remove' doesn't apply to '{target.language}' targets.", file=sys.stderr)
        if hint:
            print(f"  stoke.toml isn't the dependency manifest here — use: {hint}", file=sys.stderr)
        sys.exit(1)

    for package in packages:
        try:
            removed = remove_dep(config.config_path, target_name, package)
        except OSError as e:
            print(f"Error updating stoke.toml: {e}", file=sys.stderr)
            sys.exit(1)

        if not removed:
            print(f"Warning: '{package}' not found in stoke.toml deps for target '{target_name}'", file=sys.stderr)
            sys.exit(1)

        print(f"Removed from stoke.toml: {package} (target '{target_name}')")

    print("This only stops it from being installed on future builds.")
    print("Run 'stoke clean && stoke build' if you want it removed from the environment too.")
