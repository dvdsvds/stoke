"""npm/Node 버전 호환성 사전 점검."""
import re
import subprocess
import sys

# npm/cli#9787: Arborist #loadPeerSet의 edgesOut null 역참조 버그.
# 11.6.0에서 수정됨 -- https://github.com/npm/cli/issues/9787
_MIN_NPM_VERSION = (11, 6, 0)


def check_npm_health(npm_exe: str) -> None:
    """
    npm < 11.6.0은 peer dependency 그래프를 재귀적으로 로드할 때
    Arborist가 죽는 알려진 버그가 있음
    (예: "Cannot read properties of null (reading 'edgesOut')", npm/cli#9787).
    설치를 막지는 않고 경고만 띄워서 원인 파악 시간을 줄여줌.
    """
    try:
        result = subprocess.run(
            [npm_exe, "--version"], capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return
    if result.returncode != 0:
        return

    version = result.stdout.strip()
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        return

    if tuple(int(g) for g in match.groups()) < _MIN_NPM_VERSION:
        min_str = ".".join(str(n) for n in _MIN_NPM_VERSION)
        print(
            f"\nWarning: npm {version} detected. Known Arborist bug in peer "
            f"dependency resolution (\"Cannot read properties of null "
            f"(reading 'edgesOut')\", npm/cli#9787) can crash installs with "
            f"deep peer dependency trees on npm < {min_str}.\n"
            f"  Recommended: npm install -g npm@latest\n",
            file=sys.stderr,
        )
