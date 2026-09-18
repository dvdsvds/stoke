"""언어 버전 목록 조회 및 다운로드."""
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

from stoke.http_utils import basic_auth_headers

DEFAULT_VERSION_API_BASE = "https://dvdsvds.github.io/stoke/versions"

def get_version_api_base() -> str:
    """언어 버전 메타데이터를 가져올 base URL (STOKE_VERSION_API_BASE로 사내 미러 오버라이드 가능)."""
    return os.environ.get("STOKE_VERSION_API_BASE", DEFAULT_VERSION_API_BASE).rstrip("/")

def get_version_api_credentials() -> tuple[str | None, str | None]:
    """사설 미러 인증용 자격증명 (STOKE_VERSION_API_USER/PASSWORD, 둘 다 없으면 익명)."""
    return (
        os.environ.get("STOKE_VERSION_API_USER"),
        os.environ.get("STOKE_VERSION_API_PASSWORD"),
    )

def fetch_versions(language: str, base_url: str | None = None) -> dict:
    """언어 버전 목록 조회 (실패 시 예외, base_url 안 주면 get_version_api_base() 사용)."""
    api_base = (base_url or get_version_api_base()).rstrip("/")
    url = f"{api_base}/{language}.json"
    user, password = get_version_api_credentials()
    req = urllib.request.Request(url, headers=basic_auth_headers(user, password))
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise RuntimeError(
                f"Failed to fetch versions from {url}: HTTP 401 Unauthorized\n"
                f"  If this mirror requires auth, set STOKE_VERSION_API_USER / STOKE_VERSION_API_PASSWORD."
            )
        raise RuntimeError(f"Failed to fetch versions from {url}: HTTP {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Failed to fetch versions from {url}: {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from {url}: {e}")

def get_platform_key() -> str:
    """현재 플랫폼의 다운로드 키 반환 (리눅스는 "linux-amd64", arm64는 아직 미호스팅)."""
    if sys.platform == "win32":
        return "windows-amd64"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "linux-amd64"


def find_version(versions_data: dict, requested: str) -> dict | None:
    """요청 버전에 매칭되는 버전 정보 반환 ("latest"/"3.12"/"3.12.8" 형태 지원)."""
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