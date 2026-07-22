import hashlib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


MAVEN_CENTRAL_URL = "https://repo1.maven.org/maven2"


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
        """
        Maven Central의 상대 경로.
        예: com/google/code/gson/gson/2.10.1/gson-2.10.1.jar
        """
        group_path = self.group_id.replace(".", "/")
        return f"{group_path}/{self.artifact_id}/{self.version}/{self.jar_filename}"

    @property
    def jar_url(self) -> str:
        """JAR 파일 다운로드 URL."""
        return f"{MAVEN_CENTRAL_URL}/{self.url_path}"

    @property
    def sha1_url(self) -> str:
        """SHA-1 해시 파일 URL."""
        return f"{self.jar_url}.sha1"

    def __str__(self) -> str:
        return f"{self.group_id}:{self.artifact_id}:{self.version}"


def parse_coordinate(name: str, version: str) -> MavenCoordinate:
    """
    stoke.toml의 deps 형식을 MavenCoordinate로 변환.

    입력:
      name = "com.google.code.gson:gson"
      version = "2.10.1"

    출력:
      MavenCoordinate(group_id="com.google.code.gson", artifact_id="gson", version="2.10.1")
    """
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
    """URL에서 바이트 다운로드. 실패 시 RuntimeError."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "stoke-build"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(f"Not found: {url}")
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
) -> Path:
    """
    Maven Central에서 JAR 다운로드.
    반환: 저장된 JAR의 로컬 경로.
    실패 시 RuntimeError.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / coord.jar_filename

    # 이미 있으면 skip (SHA-1 검증만 하고 pass)
    if dest_path.exists():
        if verify_sha1:
            try:
                expected_sha1 = _download_bytes(coord.sha1_url).decode("ascii").strip().split()[0]
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
    jar_data = _download_bytes(coord.jar_url)

    # SHA-1 검증
    if verify_sha1:
        try:
            expected_sha1 = _download_bytes(coord.sha1_url).decode("ascii").strip().split()[0]
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

    # 저장
    dest_path.write_bytes(jar_data)
    return dest_path