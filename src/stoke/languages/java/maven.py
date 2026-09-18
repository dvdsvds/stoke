import hashlib
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from stoke.http_utils import basic_auth_headers

DEFAULT_MAVEN_REPO_URL = "https://repo1.maven.org/maven2"

def get_maven_repo_url() -> str:
    """JAR 다운로드에 사용할 Maven 저장소 base URL (STOKE_MAVEN_REPO_URL로 사내 미러 오버라이드 가능)."""
    return os.environ.get("STOKE_MAVEN_REPO_URL", DEFAULT_MAVEN_REPO_URL).rstrip("/")

def get_maven_credentials() -> tuple[str | None, str | None]:
    """사설 Maven 미러 인증용 자격증명 (STOKE_MAVEN_USER/PASSWORD, 둘 다 없으면 익명)."""
    return (
        os.environ.get("STOKE_MAVEN_USER"),
        os.environ.get("STOKE_MAVEN_PASSWORD"),
    )

@dataclass
class MavenCoordinate:
    """Maven 좌표: groupId:artifactId:version"""
    group_id: str
    artifact_id: str
    version: str

    @property
    def jar_filename(self) -> str:
        """예: gson-2.10.1.jar"""
        return f"{self.artifact_id}-{self.version}.jar"

    @property
    def url_path(self) -> str:
        """Maven 저장소 안에서의 상대 경로."""
        group_path = self.group_id.replace(".", "/")
        return f"{group_path}/{self.artifact_id}/{self.version}/{self.jar_filename}"

    def jar_url(self, repo_url: str | None = None) -> str:
        """JAR 파일 다운로드 URL. repo_url 안 주면 get_maven_repo_url() 사용."""
        base = (repo_url or get_maven_repo_url()).rstrip("/")
        return f"{base}/{self.url_path}"

    def sha1_url(self, repo_url: str | None = None) -> str:
        """SHA-1 해시 파일 URL."""
        return f"{self.jar_url(repo_url)}.sha1"

    def __str__(self) -> str:
        return f"{self.group_id}:{self.artifact_id}:{self.version}"

def parse_coordinate(name: str, version: str) -> MavenCoordinate:
    """stoke.toml의 deps 형식("group:artifact", version)을 MavenCoordinate로 변환."""
    if ":" not in name:
        raise ValueError(
            f"Invalid Maven coordinate: '{name}'\n"
            f"  Expected format: 'groupId:artifactId' (e.g. 'com.google.code.gson:gson')"
        )

    parts = name.split(":")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid Maven coordinate: '{name}'\n"
            f"  Expected exactly one ':' separator"
        )

    group_id, artifact_id = parts
    if not group_id or not artifact_id:
        raise ValueError(
            f"Invalid Maven coordinate: '{name}'\n"
            f"  groupId and artifactId must be non-empty"
        )

    return MavenCoordinate(
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
    )

def _download_bytes(url: str, timeout: int = 30) -> bytes:
    """URL에서 바이트 다운로드 (실패 시 RuntimeError, 필요하면 Basic Auth 헤더)."""
    user, password = get_maven_credentials()
    headers = {"User-Agent": "stoke-build"}
    headers.update(basic_auth_headers(user, password))
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(f"Not found: {url}")
        if e.code == 401:
            raise RuntimeError(
                f"HTTP 401 Unauthorized downloading {url}\n"
                f"  If this Maven repository requires auth, set STOKE_MAVEN_USER / STOKE_MAVEN_PASSWORD."
            )
        raise RuntimeError(f"HTTP {e.code} error downloading {url}: {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error downloading {url}: {e.reason}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error downloading {url}: {e}")

def _compute_sha1(data: bytes) -> str:
    """바이트의 SHA-1 해시를 hex 문자열로 반환."""
    return hashlib.sha1(data).hexdigest()

def download_jar(
    coord: MavenCoordinate,
    dest_dir: Path,
    verify_sha1: bool = True,
    repo_url: str | None = None,
) -> Path:
    """Maven 저장소에서 JAR 다운로드. 반환: 저장된 로컬 경로 (실패 시 RuntimeError)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / coord.jar_filename
    jar_url = coord.jar_url(repo_url)
    sha1_url = coord.sha1_url(repo_url)

    # 이미 있으면 skip (SHA-1 검증만 하고 pass)
    if dest_path.exists():
        if verify_sha1:
            try:
                expected_sha1 = _download_bytes(sha1_url).decode("ascii").strip().split()[0]
                actual_sha1 = _compute_sha1(dest_path.read_bytes())
                if actual_sha1 == expected_sha1:
                    return dest_path
                # 해시 불일치: 재다운로드
                print(f"  SHA-1 mismatch for {coord.jar_filename}, re-downloading...")
            except RuntimeError:
                # 해시 파일 못 받으면 그냥 기존 것 재사용
                return dest_path
        else:
            return dest_path

    # 다운로드
    print(f"  Downloading {coord}...")
    jar_data = _download_bytes(jar_url)

    # SHA-1 검증
    if verify_sha1:
        try:
            expected_sha1 = _download_bytes(sha1_url).decode("ascii").strip().split()[0]
            actual_sha1 = _compute_sha1(jar_data)
            if actual_sha1 != expected_sha1:
                raise RuntimeError(
                    f"SHA-1 verification failed for {coord}\n"
                    f"  Expected: {expected_sha1}\n"
                    f"  Actual:   {actual_sha1}"
                )
        except RuntimeError as e:
            if "Not found" in str(e):
                # SHA-1 파일 없으면 경고만
                print(f"  Warning: SHA-1 file not found for {coord}, skipping verification")
            else:
                raise

    # 저장 (같은 JAR을 동시에 받는 다른 stoke build 프로세스가 아직 다 안 쓰인
    # 파일을 dest_path.exists() 체크로 잡아가지 않도록, 임시 파일에 먼저 쓰고
    # 원자적으로 rename)
    tmp_path = dest_path.with_name(dest_path.name + f".tmp{os.getpid()}")
    tmp_path.write_bytes(jar_data)
    os.replace(tmp_path, dest_path)
    return dest_path