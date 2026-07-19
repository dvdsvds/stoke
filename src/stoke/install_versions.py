"""언어 버전 목록 조회 및 다운로드."""
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path


VERSION_API_BASE = "https://dvdsvds.github.io/stoke/versions"


def fetch_versions(language: str) -> dict:
    """
    stoke 자체 API에서 버전 목록 조회.
    실패 시 예외.
    """
    url = f"{VERSION_API_BASE}/{language}.json"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to fetch versions from {url}: {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from {url}: {e}")

def get_platform_key() -> str:
    """현재 플랫폼의 다운로드 키 반환."""
    if sys.platform == "win32":
        return "windows-amd64"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "linux"


def find_version(versions_data: dict, requested: str) -> dict | None:
    """
    요청 버전에 매칭되는 버전 정보 반환.
    requested="latest": 최신
    requested="3.12": 3.12.x 최신
    requested="3.12.8": 정확한 매칭
    """
    versions = versions_data.get("versions", [])
    if not versions:
        return None

    if requested == "latest":
        return versions[0]

    # 정확한 매칭 시도
    for v in versions:
        if v["version"] == requested:
            return v

    # major.minor 매칭 (예: "3.12" → "3.12.x" 최신)
    for v in versions:
        if v["version"].startswith(requested + "."):
            return v

    return None