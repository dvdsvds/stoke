"""stoke add/remove — python/java 의존성 추가·제거.

stoke.toml의 [targets.X.deps]가 실제 의존성 매니페스트인 언어(python/java)에서만 의미가 있음.
다른 언어는 이미 자기 생태계 도구(cargo add, npm install, go get 등)가 있고 stoke.toml이
그 매니페스트를 대체하지 않으므로 대상이 아님 — C/C++은 vcpkg 라이브러리에 한해
`stoke vcpkg install/remove`가 이미 같은 역할을 함.

javascript/typescript는 stoke.toml을 안 건드리지만, npm이 알려진 버그(edgesOut,
npm/cli#9787)가 있는 버전이면 그냥 npm을 그대로 실행해서 죽는 것보다 stoke가
대신 install 명령을 실행해주는 게 낫다고 판단해 npm_check로 우회 실행함.
"""
import shutil
import subprocess
import sys
from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit
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

def _npm_add(config, package: str, version: str | None) -> None:
    """javascript/typescript: stoke.toml 대신 실제 npm install을 실행 (npm 버그 우회 포함)."""
    from stoke.npm_check import resolve_npm_command

    npm_exe = shutil.which("npm")
    if npm_exe is None:
        print("Error: npm not found in PATH.", file=sys.stderr)
        sys.exit(1)

    spec = f"{package}@{version}" if version else package
    print(f"Running: npm install {spec}\n")
    result = subprocess.run(
        resolve_npm_command(npm_exe) + ["install", spec],
        cwd=str(config.config_path.parent),
    )
    if result.returncode != 0:
        print(f"Error: npm install {spec} failed", file=sys.stderr)
        sys.exit(1)

def cmd_add_dep(package: str, version: str | None, target_name: str | None):
    """stoke add <package> [version] [--target=X]"""
    config = load_config_or_exit()
    target_name = resolve_target_or_exit(config, target_name, verb="adding to")
    target = config.targets[target_name]

    if target.language in _NPM_LANGUAGES:
        _npm_add(config, package, version)
        return

    if target.language not in _MANAGED_LANGUAGES:
        hint = _NATIVE_HINT.get(target.language)
        print(f"Error: 'stoke add' doesn't apply to '{target.language}' targets.", file=sys.stderr)
        if hint:
            print(f"  stoke.toml isn't the dependency manifest here — use: {hint}", file=sys.stderr)
        sys.exit(1)

    if target.language == "java" and not version:
        print("Error: Java dependencies need an explicit version.", file=sys.stderr)
        print(f"  stoke add {package} <version> [--target={target_name}]", file=sys.stderr)
        sys.exit(1)

    resolved_version = version or "*"
    try:
        add_dep(config.config_path, target_name, package, resolved_version)
    except OSError as e:
        print(f"Error updating stoke.toml: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Added to stoke.toml: {package} = \"{resolved_version}\" (target '{target_name}')\n")

    from stoke.cli.build import cmd_build
    cmd_build(target_name)

def cmd_remove_dep(package: str, target_name: str | None):
    """stoke remove <package> [--target=X]"""
    config = load_config_or_exit()
    target_name = resolve_target_or_exit(config, target_name, verb="removing from")
    target = config.targets[target_name]

    if target.language not in _MANAGED_LANGUAGES:
        hint = _NATIVE_HINT.get(target.language)
        print(f"Error: 'stoke remove' doesn't apply to '{target.language}' targets.", file=sys.stderr)
        if hint:
            print(f"  stoke.toml isn't the dependency manifest here — use: {hint}", file=sys.stderr)
        sys.exit(1)

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
