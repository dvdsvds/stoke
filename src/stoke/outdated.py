"""stoke outdated -- 의존성이 최신 버전 대비 얼마나 뒤처졌는지 확인 (CVE 여부와는 별개 질문)."""
import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from stoke.languages.java.maven import get_maven_credentials, get_maven_repo_url
from stoke.http_utils import basic_auth_headers

def pypi_latest(name: str, timeout: int = 15) -> str | None:
    """PyPI JSON API로 최신 버전 조회. 실패하면 None (네트워크 오류/패키지 없음 등)."""
    url = f"https://pypi.org/pypi/{name}/json"
    req = urllib.request.Request(url, headers={"User-Agent": "stoke-outdated"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read())
        return data.get("info", {}).get("version")
    except Exception:
        return None

def maven_latest(group_artifact: str, timeout: int = 15) -> str | None:
    """group:artifact의 maven-metadata.xml에서 최신(release) 버전 조회. 실패하면 None."""
    if ":" not in group_artifact:
        return None
    group_id, artifact_id = group_artifact.split(":", 1)
    group_path = group_id.replace(".", "/")
    url = f"{get_maven_repo_url()}/{group_path}/{artifact_id}/maven-metadata.xml"

    user, password = get_maven_credentials()
    headers = {"User-Agent": "stoke-outdated"}
    headers.update(basic_auth_headers(user, password))
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            root = ET.fromstring(response.read())
    except Exception:
        return None

    versioning = root.find("versioning")
    if versioning is None:
        return None
    release = versioning.findtext("release") or versioning.findtext("latest")
    return release
