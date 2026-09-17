"""npm 버전 호환성 점검 및 우회.

전역 npm이 알려진 버그를 갖고 있어도, stoke는 시스템 전역 상태를 건드리지
않는다는 원칙(언어/툴체인을 프로젝트별로 격리)을 따른다. 그래서 전역 npm을
업그레이드하라고 안내하는 대신, npx로 그 install 한 번만 고쳐진 버전의
npm을 즉석에서 받아써서 우회한다.
"""
import json
import re
import shutil
import subprocess
import sys

# npm/cli#9787: Arborist #loadPeerSet의 edgesOut null 역참조 버그.
# 11.6.0에서 수정됨 -- https://github.com/npm/cli/issues/9787
_MIN_NPM_VERSION = (11, 6, 0)

Version = tuple[int, int, int]


def _parse_version(text: str) -> Version | None:
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", text.strip())
    if not match:
        return None
    return tuple(int(g) for g in match.groups())  # type: ignore[return-value]


def _parse_comparator(comp: str):
    """단일 semver 비교식('^X.Y.Z', '>=X.Y.Z' 등)을 판별 함수로 변환."""
    comp = comp.strip()
    for op, width in ((">=", 2), ("<=", 2), (">", 1), ("<", 1), ("=", 1)):
        if comp.startswith(op):
            target = _parse_version(comp[width:])
            if target is None:
                return None
            if op == ">=":
                return lambda v: v >= target
            if op == "<=":
                return lambda v: v <= target
            if op == ">":
                return lambda v: v > target
            if op == "<":
                return lambda v: v < target
            return lambda v: v == target
    if comp.startswith("^"):
        target = _parse_version(comp[1:])
        if target is None:
            return None
        major, minor, patch = target
        if major > 0:
            upper = (major + 1, 0, 0)
        elif minor > 0:
            upper = (0, minor + 1, 0)
        else:
            upper = (0, 0, patch + 1)
        return lambda v: target <= v < upper
    target = _parse_version(comp)
    if target is None:
        return None
    return lambda v: v == target


def _satisfies(version: Version, range_str: str) -> bool:
    """'^20.17.0 || >=22.9.0' 같은 npm engines.node 범위 문자열을 평가."""
    for comparator_set in range_str.split("||"):
        checks = [_parse_comparator(c) for c in comparator_set.split()]
        if all(c is not None for c in checks) and all(c(version) for c in checks):
            return True
    return False


def _recommend_npm_version(npm_exe: str, node_version: Version) -> str | None:
    """MIN_NPM_VERSION 이상이면서 현재 Node와 호환되는 npm 중 최신 버전을 찾음."""
    try:
        result = subprocess.run(
            [npm_exe, "view", f"npm@>={'.'.join(map(str, _MIN_NPM_VERSION))}",
             "version", "engines", "--json"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return None
        entries = json.loads(result.stdout)
    except Exception:
        return None

    best: tuple[Version, str] | None = None
    for entry in entries:
        version = _parse_version(entry.get("version", ""))
        node_range = (entry.get("engines") or {}).get("node")
        if version is None or not node_range:
            continue
        if not _satisfies(node_version, node_range):
            continue
        if best is None or version > best[0]:
            best = (version, entry["version"])
    return best[1] if best else None


def _check(npm_exe: str) -> tuple[str, Version | None, Version | None, str | None]:
    """(버전 문자열, 파싱된 버전, Node 버전, 현재 Node와 호환되는 고쳐진 npm 버전) 반환.
    npm이 정상이거나 확인할 수 없으면 파싱된 버전이 None이거나 MIN 이상."""
    try:
        result = subprocess.run(
            [npm_exe, "--version"], capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return "", None, None, None
    if result.returncode != 0:
        return "", None, None, None

    version_str = result.stdout.strip()
    version = _parse_version(version_str)
    if version is None or version >= _MIN_NPM_VERSION:
        return version_str, version, None, None

    node_exe = shutil.which("node")
    node_version = None
    if node_exe:
        try:
            node_result = subprocess.run(
                [node_exe, "--version"], capture_output=True, text=True, timeout=10,
            )
            if node_result.returncode == 0:
                node_version = _parse_version(node_result.stdout)
        except Exception:
            node_version = None

    recommended_version = (
        _recommend_npm_version(npm_exe, node_version) if node_version else None
    )
    return version_str, version, node_version, recommended_version


def resolve_npm_command(npm_exe: str) -> list[str]:
    """이번 호출에 쓸 npm 커맨드 프리픽스를 반환한다 (뒤에 "install" 등을 붙여 씀).

    npm이 정상이면 [npm_exe] 그대로. 버그 있는 버전(< 11.6.0)이면, 현재 Node와
    호환되는 고쳐진 버전을 찾아 `npx -y npm@<version>`으로 그 한 번만 우회 --
    전역 npm은 건드리지 않는다. 호환되는 고쳐진 버전을 못 찾으면(Node 자체가
    너무 오래됨) 경고만 띄우고 기존 npm_exe로 진행한다.
    """
    version_str, version, node_version, recommended_version = _check(npm_exe)
    if version is None or version >= _MIN_NPM_VERSION:
        return [npm_exe]

    min_str = ".".join(str(n) for n in _MIN_NPM_VERSION)
    npx_exe = shutil.which("npx")

    if recommended_version and npx_exe:
        print(
            f"\nWarning: npm {version_str} has a known Arborist bug in peer "
            f"dependency resolution (\"Cannot read properties of null "
            f"(reading 'edgesOut')\", npm/cli#9787), fixed in npm {min_str}.\n"
            f"  Using npx npm@{recommended_version} for this install "
            f"(global npm left untouched).\n",
            file=sys.stderr,
        )
        return [npx_exe, "-y", f"npm@{recommended_version}"]

    print(
        f"\nWarning: npm {version_str} detected. {_warning_detail(min_str, node_version, recommended_version)}\n",
        file=sys.stderr,
    )
    return [npm_exe]


def warn_npm_health(npm_exe: str) -> None:
    """커맨드를 바꿔치기할 수 없는 경우(써드파티 CLI가 자체적으로 system npm을
    호출하는 경우 등)에 진단 경고만 출력한다."""
    version_str, version, node_version, recommended_version = _check(npm_exe)
    if version is None or version >= _MIN_NPM_VERSION:
        return

    min_str = ".".join(str(n) for n in _MIN_NPM_VERSION)
    print(
        f"\nWarning: npm {version_str} detected. {_warning_detail(min_str, node_version, recommended_version)}\n",
        file=sys.stderr,
    )


def _warning_detail(min_str: str, node_version: Version | None, recommended_version: str | None) -> str:
    base = (
        f"Known Arborist bug in peer dependency resolution "
        f"(\"Cannot read properties of null (reading 'edgesOut')\", npm/cli#9787) "
        f"can crash installs with deep peer dependency trees on npm < {min_str}."
    )
    if recommended_version:
        return f"{base}\n  Recommended: npm install -g npm@{recommended_version}"
    if node_version is not None:
        return (
            f"{base}\n  No npm >= {min_str} is compatible with your Node "
            f"{'.'.join(map(str, node_version))} -- upgrade Node first."
        )
    return f"{base}\n  Recommended: npm install -g npm@latest"
