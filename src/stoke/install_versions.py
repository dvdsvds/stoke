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
    """
    버전 메타데이터(각 언어의 다운로드 가능 버전 목록)를 가져올 base URL.

    STOKE_VERSION_API_BASE 환경변수로 오버라이드 가능. 외부 인터넷을
    화이트리스트로만 열어둔 사내망에서는 stoke 기본 GitHub Pages
    엔드포인트에 못 닿을 수 있어서, 같은 JSON 스키마로 사내 미러 서버를
    운영하고 이 env var로 가리키게 하기 위함.
    """
    return os.environ.get("STOKE_VERSION_API_BASE", DEFAULT_VERSION_API_BASE).rstrip("/")

def get_version_api_credentials() -> tuple[str | None, str | None]:
    """
    사설 미러가 인증을 요구할 때 쓸 자격증명.
    STOKE_VERSION_API_USER / STOKE_VERSION_API_PASSWORD 환경변수로 설정.
    둘 다 없으면 (None, None) — 익명 요청 (기존 동작과 동일한 하위 호환).
    """
    return (
        os.environ.get("STOKE_VERSION_API_USER"),
        os.environ.get("STOKE_VERSION_API_PASSWORD"),
    )

def fetch_versions(language: str, base_url: str | None = None) -> dict:
    """
    언어 버전 목록 조회. 실패 시 예외.
    base_url을 안 주면 get_version_api_base() 결과 사용
    (STOKE_VERSION_API_BASE 환경변수 또는 stoke 기본 엔드포인트).
    STOKE_VERSION_API_USER/PASSWORD가 설정돼 있으면 Basic Auth 헤더를 붙임.
    """
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