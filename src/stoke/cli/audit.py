"""stoke audit -- 언어별 취약점 스캐너로 위임 (python/java는 lock 파일 기준 OSV.dev 직접 조회)."""
import json
import shutil
import subprocess
import sys

from stoke.cli._dep_check import emit_raw_json, find_csproj, find_dotnet, json_wrapped_external
from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit
from stoke.lock import load_lock
from stoke.osv import query_batch

_UNSUPPORTED = {
    "kotlin": "no single standard CLI for this yet (see the OWASP Dependency-Check Gradle plugin: https://github.com/dependency-check/dependency-check-gradle)",
    "c": "vcpkg has no vulnerability database to check against",
    "cpp": "vcpkg has no vulnerability database to check against",
}

def _emit_osv_json(ecosystem: str, found: dict) -> None:
    vulnerabilities = [
        {"package": name, "id": vuln.id, "summary": vuln.summary, "url": f"https://osv.dev/vulnerability/{vuln.id}"}
        for name, vulns in sorted(found.items()) for vuln in vulns
    ]
    print(json.dumps({
        "ecosystem": ecosystem,
        "vulnerable": bool(vulnerabilities),
        "vulnerability_count": len(vulnerabilities),
        "vulnerabilities": vulnerabilities,
    }, indent=2))

def _print_osv_result(ecosystem: str, found: dict) -> bool:
    """취약점 있으면 출력하고 True, 없으면 '취약점 없음' 출력하고 False."""
    if not found:
        print(f"No known vulnerabilities found ({ecosystem}).")
        return False

    total = sum(len(vulns) for vulns in found.values())
    print(f"Found {total} known vulnerabilit{'y' if total == 1 else 'ies'} in {len(found)} package(s):\n")
    for name, vulns in sorted(found.items()):
        for vuln in vulns:
            summary = f" — {vuln.summary}" if vuln.summary else ""
            print(f"  {name}: {vuln.id}{summary}")
            print(f"    https://osv.dev/vulnerability/{vuln.id}")
    return True

def _audit_python(config, target, json_output: bool) -> int:
    lock = load_lock(config.config_path.parent, config.project.lock_mode)
    if lock is None or not lock.packages:
        print("No lock file with resolved package versions found. Run 'stoke build' first.", file=sys.stderr)
        return 1
    found = query_batch("PyPI", lock.packages)
    if json_output:
        _emit_osv_json("PyPI", found)
        return 1 if found else 0
    return 1 if _print_osv_result("PyPI", found) else 0

def _audit_java(config, target, json_output: bool) -> int:
    lock = load_lock(config.config_path.parent, config.project.lock_mode)
    if lock is None or not lock.java_deps:
        print("No lock file with resolved dependency versions found. Run 'stoke build' first.", file=sys.stderr)
        return 1
    packages = {name: dep.version for name, dep in lock.java_deps.items()}
    found = query_batch("Maven", packages)
    if json_output:
        _emit_osv_json("Maven", found)
        return 1 if found else 0
    return 1 if _print_osv_result("Maven", found) else 0

def _audit_npm(config, target, json_output: bool) -> int:
    from stoke.languages._node_tools import find_npm
    from stoke.npm_check import resolve_npm_command

    project_root = config.config_path.parent
    try:
        npm_exe = find_npm(project_root)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    cmd = resolve_npm_command(npm_exe) + ["audit"] + (["--json"] if json_output else [])
    if not json_output:
        result = subprocess.run(cmd, cwd=str(project_root))
        return result.returncode

    result = subprocess.run(cmd, cwd=str(project_root), capture_output=True, text=True, errors="replace")
    print(result.stdout, end="")
    # npm audit는 취약점이 있으면 exit 1 -- stdout의 JSON 자체는 그대로 유효하니 그냥 통과
    return result.returncode

def _audit_composer(config, target, json_output: bool) -> int:
    composer_exe = shutil.which("composer")
    if composer_exe is None:
        print("Error: composer not found in PATH.\n  Install from: https://getcomposer.org/download/", file=sys.stderr)
        return 1
    cmd = [composer_exe, "audit"] + (["--format=json"] if json_output else [])
    if not json_output:
        result = subprocess.run(cmd, cwd=str(config.config_path.parent))
        return result.returncode

    result = subprocess.run(cmd, cwd=str(config.config_path.parent), capture_output=True, text=True, errors="replace")
    print(result.stdout, end="")
    return result.returncode

def _audit_dotnet(config, target, json_output: bool) -> int:
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
    cmd = [dotnet_exe, "list", "package", "--vulnerable", "--include-transitive"]
    if csproj is not None:
        cmd.insert(2, str(csproj))

    result = subprocess.run(cmd, cwd=str(project_root), env=env, capture_output=True, text=True, errors="replace")
    vulnerable = "has the following vulnerable packages" in result.stdout

    if json_output:
        emit_raw_json("csharp", result.returncode, result.stdout + result.stderr)
        return result.returncode if result.returncode != 0 else (1 if vulnerable else 0)

    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode != 0:
        return result.returncode
    return 1 if vulnerable else 0

def _audit_go(config, target, json_output: bool) -> int:
    return json_wrapped_external(
        "go", "govulncheck", "govulncheck", "go install golang.org/x/vuln/cmd/govulncheck@latest",
        lambda exe: [exe, "./..."], config.config_path.parent, json_output,
    )

def _audit_rust(config, target, json_output: bool) -> int:
    return json_wrapped_external(
        "rust", "cargo-audit", "cargo-audit", "cargo install cargo-audit",
        lambda exe: [exe, "audit"], config.config_path.parent, json_output,
    )

def _audit_ruby(config, target, json_output: bool) -> int:
    bundle_name = "bundle.bat" if sys.platform == "win32" else "bundle"
    return json_wrapped_external(
        "ruby", bundle_name, "bundler-audit", "gem install bundler-audit",
        lambda exe: [exe, "exec", "bundle-audit", "check", "--update"], config.config_path.parent, json_output,
    )

_AUDITORS = {
    "python": _audit_python,
    "java": _audit_java,
    "javascript": _audit_npm,
    "typescript": _audit_npm,
    "php": _audit_composer,
    "csharp": _audit_dotnet,
    "go": _audit_go,
    "rust": _audit_rust,
    "ruby": _audit_ruby,
}

def cmd_audit(target_name: str | None, json_output: bool = False) -> None:
    """stoke audit [--target=X] [--json] -- 대상 언어의 의존성을 알려진 취약점(CVE)과 대조."""
    config = load_config_or_exit()
    target_name = resolve_target_or_exit(config, target_name, verb="auditing")
    target = config.targets[target_name]

    if target.language in _UNSUPPORTED:
        print(f"'stoke audit' doesn't support '{target.language}' yet: {_UNSUPPORTED[target.language]}", file=sys.stderr)
        sys.exit(1)

    auditor = _AUDITORS.get(target.language)
    if auditor is None:
        print(f"'stoke audit' doesn't support '{target.language}' yet.", file=sys.stderr)
        sys.exit(1)

    sys.exit(auditor(config, target, json_output))
