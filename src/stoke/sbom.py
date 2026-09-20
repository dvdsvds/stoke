"""SBOM(Software Bill of Materials) 생성 -- 언어별로 의존성 이름/버전을 모아서 purl까지 붙여줌."""
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from stoke.lock import load_lock

@dataclass
class Component:
    name: str
    version: str
    purl: str

def _normalize_pypi_name(name: str) -> str:
    """PEP 503 정규화 (purl 규격이 pypi 이름은 소문자+하이픈으로 정규화하길 요구)."""
    return re.sub(r"[-_.]+", "-", name.lower())

def collect_python(config, target) -> list[Component]:
    lock = load_lock(config.config_path.parent, config.project.lock_mode)
    if lock is None or not lock.packages:
        return []
    return [
        Component(name=name, version=version, purl=f"pkg:pypi/{_normalize_pypi_name(name)}@{version}")
        for name, version in sorted(lock.packages.items())
    ]

def collect_java(config, target) -> list[Component]:
    lock = load_lock(config.config_path.parent, config.project.lock_mode)
    if lock is None or not lock.java_deps:
        return []
    components = []
    for name, dep in sorted(lock.java_deps.items()):
        group, _, artifact = name.partition(":")
        components.append(Component(name=name, version=dep.version, purl=f"pkg:maven/{group}/{artifact}@{dep.version}"))
    return components

def collect_npm(project_root: Path) -> list[Component]:
    """`npm ls --all --json`로 설치된 트리를 재귀적으로 펼쳐서 이름/버전 dedupe."""
    from stoke.languages._node_tools import find_npm
    from stoke.npm_check import resolve_npm_command

    try:
        npm_exe = find_npm(project_root)
    except RuntimeError:
        return []

    result = subprocess.run(
        resolve_npm_command(npm_exe) + ["ls", "--all", "--json"],
        cwd=str(project_root), capture_output=True, text=True, errors="replace",
    )
    if not result.stdout.strip():
        return []
    try:
        tree = json.loads(result.stdout)
    except ValueError:
        return []

    seen: dict[str, str] = {}

    def _walk(deps: dict) -> None:
        for name, info in (deps or {}).items():
            version = info.get("version")
            if version:
                seen[name] = version
            _walk(info.get("dependencies"))

    _walk(tree.get("dependencies"))

    components = []
    for name, version in sorted(seen.items()):
        purl_name = name.replace("@", "%40", 1) if name.startswith("@") else name
        components.append(Component(name=name, version=version, purl=f"pkg:npm/{purl_name}@{version}"))
    return components

def collect_go(project_root: Path) -> list[Component]:
    """`go list -m -json all` -- 개행 없이 이어붙은 JSON 오브젝트 여러 개라 raw_decode로 하나씩 뜯음."""
    result = subprocess.run(
        ["go", "list", "-m", "-json", "all"],
        cwd=str(project_root), capture_output=True, text=True, errors="replace",
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []

    decoder = json.JSONDecoder()
    text = result.stdout
    pos = 0
    components = []
    while pos < len(text):
        text_from_pos = text[pos:].lstrip()
        if not text_from_pos:
            break
        pos = len(text) - len(text_from_pos)
        obj, end = decoder.raw_decode(text, pos)
        pos = end
        if obj.get("Main") or not obj.get("Version"):
            continue
        name, version = obj["Path"], obj["Version"]
        components.append(Component(name=name, version=version, purl=f"pkg:golang/{name}@{version}"))
    return components

def collect_rust(project_root: Path) -> list[Component]:
    """`cargo metadata` -- source가 있는(=외부 registry) 패키지만 의존성으로 취급, 워크스페이스 멤버는 제외."""
    result = subprocess.run(
        ["cargo", "metadata", "--format-version=1"],
        cwd=str(project_root), capture_output=True, text=True, errors="replace",
    )
    if result.returncode != 0 or not result.stdout.strip():
        return []
    try:
        data = json.loads(result.stdout)
    except ValueError:
        return []

    components = []
    for pkg in data.get("packages", []):
        if pkg.get("source") is None:
            continue
        name, version = pkg["name"], pkg["version"]
        components.append(Component(name=name, version=version, purl=f"pkg:cargo/{name}@{version}"))
    return components
