"""JS/TS 공용 Node 버전 pin 로직."""
import json
from pathlib import Path

from stoke.prompts import _prompt

def _select_node_version() -> str:
    """선택적 Node 버전 pin (빈 입력이면 pin 안 함)."""
    return _prompt(
        "Pin Node version? (e.g. 20.11.0, blank to skip)", default=""
    ).strip()

def _pin_node_version(project_root: Path, version: str) -> None:
    """.nvmrc + package.json의 engines.node를 씀 (소프트 pin, 빈 문자열이면 아무것도 안 함)."""
    if not version:
        return

    (project_root / ".nvmrc").write_text(version + "\n", encoding="utf-8")

    package_json = project_root / "package.json"
    if package_json.is_file():
        pkg = json.loads(package_json.read_text(encoding="utf-8"))
        pkg.setdefault("engines", {})["node"] = f">={version}"
        package_json.write_text(json.dumps(pkg, indent=2) + "\n", encoding="utf-8")
