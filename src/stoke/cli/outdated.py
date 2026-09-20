"""stoke outdated -- 의존성이 최신 버전 대비 얼마나 뒤처졌는지 확인 (CVE 여부와는 별개, stoke audit과 대응)."""
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from stoke.cli._dep_check import emit_raw_json, find_csproj, find_dotnet, json_wrapped_external
from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit
from stoke.lock import load_lock
from stoke.outdated import maven_latest, pypi_latest

_UNSUPPORTED = {
    "kotlin": "no single standard CLI for this yet",
    "c": "vcpkg doesn't expose per-library update info stoke can query yet",
    "cpp": "vcpkg doesn't expose per-library update info stoke can query yet",
}

_MAX_WORKERS = 8

def _collect_outdated(names_and_versions: dict, latest_lookup) -> dict:
    items = sorted(names_and_versions.items())
    if not items:
        return {}
    with ThreadPoolExecutor(max_workers=min(_MAX_WORKERS, len(items))) as pool:
        latests = pool.map(lambda item: latest_lookup(item[0]), items)
        outdated = {}
        for (name, current), latest in zip(items, latests):
            if latest is not None and latest != current:
                outdated[name] = (current, latest)
    return outdated

def _print_outdated(total: int, outdated: dict) -> bool:
    if not outdated:
        print(f"All {total} package(s) up to date.")
        return False
    print(f"{len(outdated)} of {total} package(s) outdated:\n")
    for name, (current, latest) in outdated.items():
        print(f"  {name}: {current} -> {latest}")
    return True

def _emit_outdated_json(total: int, outdated: dict) -> None:
    print(json.dumps({
        "package_count": total,
        "outdated_count": len(outdated),
        "outdated": [
            {"package": name, "current": current, "latest": latest}
            for name, (current, latest) in outdated.items()
        ],
    }, indent=2))

def _outdated_python(config, target, json_output: bool) -> int:
    lock = load_lock(config.config_path.parent, config.project.lock_mode)
    if lock is None or not lock.packages:
        print("No lock file with resolved package versions found. Run 'stoke build' first.", file=sys.stderr)
        return 1
    outdated = _collect_outdated(lock.packages, pypi_latest)
    if json_output:
        _emit_outdated_json(len(lock.packages), outdated)
        return 1 if outdated else 0
    return 1 if _print_outdated(len(lock.packages), outdated) else 0

def _outdated_java(config, target, json_output: bool) -> int:
    lock = load_lock(config.config_path.parent, config.project.lock_mode)
    if lock is None or not lock.java_deps:
        print("No lock file with resolved dependency versions found. Run 'stoke build' first.", file=sys.stderr)
        return 1
    packages = {name: dep.version for name, dep in lock.java_deps.items()}
    outdated = _collect_outdated(packages, maven_latest)
    if json_output:
        _emit_outdated_json(len(packages), outdated)
        return 1 if outdated else 0
    return 1 if _print_outdated(len(packages), outdated) else 0

def _outdated_npm(config, target, json_output: bool) -> int:
    from stoke.languages._node_tools import find_npm
    from stoke.npm_check import resolve_npm_command

    project_root = config.config_path.parent
    try:
        npm_exe = find_npm(project_root)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    cmd = resolve_npm_command(npm_exe) + ["outdated"] + (["--json"] if json_output else [])
    if not json_output:
        # npm outdated는 뒤처진 패키지가 있으면 exit code 1을 씀 (npm audit과 동일한 관례)
        result = subprocess.run(cmd, cwd=str(project_root))
        return result.returncode

    result = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True, errors="replace")
    print(result.stdout, end="")
    return result.returncode

def _outdated_composer(config, target, json_output: bool) -> int:
    composer_exe = shutil.which("composer")
    if composer_exe is None:
        print("Error: composer not found in PATH.\n  Install from: https://getcomposer.org/download/", file=sys.stderr)
        return 1
    cmd = [composer_exe, "outdated", "--direct"] + (["--format=json"] if json_output else [])
    result = subprocess.run(
        cmd, cwd=str(config.config_path.parent), capture_output=True, text=True, errors="replace",
    )
    print(result.stdout, end="")
    if not json_output and result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return 1 if result.stdout.strip() else 0

def _outdated_dotnet(config, target, json_output: bool) -> int:
    project_root = config.config_path.parent
    dotnet_exe, env = find_dotnet(project_root)
    if dotnet_exe is None:
        msg = "dotnet not found.\n  Install .NET SDK from: https://dotnet.microsoft.com/download"
        if json_output:
            print(json.dumps({"language": "csharp", "structured": False, "error": msg}, indent=2))
        else:
            print(f"Error: {msg}", file=sys.stderr)
        return 1

    csproj = find_csproj(project_root, target.name)
    cmd = [dotnet_exe, "list", "package", "--outdated"]
    if csproj is not None:
        cmd.insert(2, str(csproj))

    result = subprocess.run(cmd, cwd=str(project_root), env=env, capture_output=True, text=True, errors="replace")
    has_updates = "There are no updates given the current constraints" not in result.stdout

    if json_output:
        emit_raw_json("csharp", result.returncode, result.stdout + result.stderr)
        return result.returncode if result.returncode != 0 else (1 if has_updates else 0)

    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode != 0:
        return result.returncode
    return 1 if has_updates else 0

def _outdated_go(config, target, json_output: bool) -> int:
    return json_wrapped_external(
        "go", ("go", "go.exe"), "Go", "stoke install go",
        lambda exe: [exe, "list", "-u", "-m", "all"], config.config_path.parent, json_output,
    )

def _outdated_rust(config, target, json_output: bool) -> int:
    return json_wrapped_external(
        "rust", "cargo-outdated", "cargo-outdated", "cargo install cargo-outdated",
        lambda exe: [exe, "outdated"], config.config_path.parent, json_output,
    )

def _outdated_ruby(config, target, json_output: bool) -> int:
    bundle_name = "bundle.bat" if sys.platform == "win32" else "bundle"
    return json_wrapped_external(
        "ruby", bundle_name, "Bundler", "gem install bundler",
        lambda exe: [exe, "outdated"], config.config_path.parent, json_output,
    )

_CHECKERS = {
    "python": _outdated_python,
    "java": _outdated_java,
    "javascript": _outdated_npm,
    "typescript": _outdated_npm,
    "php": _outdated_composer,
    "csharp": _outdated_dotnet,
    "go": _outdated_go,
    "rust": _outdated_rust,
    "ruby": _outdated_ruby,
}

def cmd_outdated(target_name: str | None, json_output: bool = False) -> None:
    """stoke outdated [--target=X] [--json] -- 대상 언어의 의존성이 최신 버전 대비 뒤처졌는지 확인."""
    config = load_config_or_exit()
    target_name = resolve_target_or_exit(config, target_name, verb="checking")
    target = config.targets[target_name]

    if target.language in _UNSUPPORTED:
        print(f"'stoke outdated' doesn't support '{target.language}' yet: {_UNSUPPORTED[target.language]}", file=sys.stderr)
        sys.exit(1)

    checker = _CHECKERS.get(target.language)
    if checker is None:
        print(f"'stoke outdated' doesn't support '{target.language}' yet.", file=sys.stderr)
        sys.exit(1)

    sys.exit(checker(config, target, json_output))
