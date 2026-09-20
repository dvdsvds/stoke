"""stoke sbom -- CycloneDX/SPDX 포맷으로 SBOM(의존성 성분표) 파일 생성.

포맷 종류:
- CycloneDX: OWASP가 만든 포맷. JSON/XML, 스키마가 비교적 단순해서 Dependency-Track/Grype 같은
  보안 스캐너 생태계에서 널리 쓰임. 기본값.
- SPDX: Linux Foundation이 만든 포맷 (ISO/IEC 5962:2021 국제표준). 원래 라이선스 컴플라이언스용으로
  시작돼서 더 무겁고 formal한 스키마. 정부 조달/컴플라이언스 요구사항에서 CycloneDX와 나란히
  요구되는 경우가 많음 (예: 미국 NTIA의 SBOM 최소 요소 기준이 둘 다 인정).
"""
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from stoke import __version__
from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit
from stoke.sbom import Component, collect_go, collect_java, collect_npm, collect_python, collect_rust

_UNSUPPORTED = {
    "kotlin": "no single standard CLI for this yet",
    "csharp": "not yet supported",
    "ruby": "not yet supported",
    "php": "not yet supported",
    "c": "vcpkg dependency listing not wired up yet",
    "cpp": "vcpkg dependency listing not wired up yet",
}

_COLLECTORS = {
    "python": lambda config, target: collect_python(config, target),
    "java": lambda config, target: collect_java(config, target),
    "javascript": lambda config, target: collect_npm(config.config_path.parent),
    "typescript": lambda config, target: collect_npm(config.config_path.parent),
    "go": lambda config, target: collect_go(config.config_path.parent),
    "rust": lambda config, target: collect_rust(config.config_path.parent),
}

def _build_cyclonedx(project_name: str, project_version: str, components: list[Component]) -> dict:
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": [{"vendor": "stoke", "name": "stoke", "version": __version__}],
            "component": {"type": "application", "name": project_name, "version": project_version},
        },
        "components": [
            {"type": "library", "name": c.name, "version": c.version, "purl": c.purl}
            for c in components
        ],
    }

def _build_spdx(project_name: str, components: list[Component]) -> dict:
    doc_id = uuid.uuid4()
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": project_name,
        "documentNamespace": f"https://stoke.dev/spdxdocs/{project_name}-{doc_id}",
        "creationInfo": {
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "creators": [f"Tool: stoke-{__version__}"],
        },
        "packages": [
            {
                "SPDXID": f"SPDXRef-Package-{i}",
                "name": c.name,
                "versionInfo": c.version,
                "downloadLocation": "NOASSERTION",
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "externalRefs": [{
                    "referenceCategory": "PACKAGE-MANAGER",
                    "referenceType": "purl",
                    "referenceLocator": c.purl,
                }],
            }
            for i, c in enumerate(components, start=1)
        ],
    }

def cmd_sbom(target_name: str | None, format_: str, output: str | None) -> None:
    """stoke sbom [--target=X] [--format=cyclonedx|spdx] [--output=path|-]"""
    if format_ not in ("cyclonedx", "spdx"):
        print(f"Error: unknown --format '{format_}' (must be 'cyclonedx' or 'spdx')", file=sys.stderr)
        sys.exit(1)

    config = load_config_or_exit()
    target_name = resolve_target_or_exit(config, target_name, verb="generating an SBOM for")
    target = config.targets[target_name]

    if target.language in _UNSUPPORTED:
        print(f"'stoke sbom' doesn't support '{target.language}' yet: {_UNSUPPORTED[target.language]}", file=sys.stderr)
        sys.exit(1)

    collector = _COLLECTORS.get(target.language)
    if collector is None:
        print(f"'stoke sbom' doesn't support '{target.language}' yet.", file=sys.stderr)
        sys.exit(1)

    components = collector(config, target)
    if format_ == "cyclonedx":
        doc = _build_cyclonedx(config.project.name, config.project.version, components)
        default_name = "sbom.cdx.json"
    else:
        doc = _build_spdx(config.project.name, components)
        default_name = "sbom.spdx.json"

    text = json.dumps(doc, indent=2) + "\n"

    if output == "-":
        print(text, end="")
        return

    out_path = Path(output) if output else config.config_path.parent / default_name
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {len(components)} component(s) to {out_path}")
