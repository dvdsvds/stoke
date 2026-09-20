"""원격/공유 빌드 캐시 -- 디렉토리 공유(STOKE_REMOTE_CACHE_DIR) 또는 HTTP 서버(STOKE_REMOTE_CACHE_URL).

둘 다 헤더까지 content-hash로 검증하고, 어떤 실패든(네트워크 오류, 디스크 오류, 인증 실패, 서버 다운) 조용히
캐시 미스로 취급함 -- 원격 캐시는 있으면 빠르고 없어도 빌드가 깨지면 안 됨(fail open).
"""
import hashlib
import io
import json
import os
import shutil
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

from stoke.cache import get_file_stat, FileStat
from stoke.http_utils import basic_auth_headers

_HTTP_TIMEOUT = 10

class DirCacheBackend:
    """STOKE_REMOTE_CACHE_DIR -- 네트워크 드라이브 등 공유 디렉토리."""
    def __init__(self, path: Path):
        self.path = path

class HttpCacheBackend:
    """STOKE_REMOTE_CACHE_URL -- HTTP로 접근하는 캐시 서버 (사내망 밖 원격 팀/클라우드 CI용)."""
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        user = os.environ.get("STOKE_REMOTE_CACHE_USER")
        password = os.environ.get("STOKE_REMOTE_CACHE_PASSWORD")
        self.headers = basic_auth_headers(user, password)

def get_remote_cache_backend() -> DirCacheBackend | HttpCacheBackend | None:
    """STOKE_REMOTE_CACHE_URL이 있으면 HTTP, 없으면 STOKE_REMOTE_CACHE_DIR, 둘 다 없으면 None."""
    url = os.environ.get("STOKE_REMOTE_CACHE_URL")
    if url:
        return HttpCacheBackend(url)
    dir_value = os.environ.get("STOKE_REMOTE_CACHE_DIR")
    return DirCacheBackend(Path(dir_value)) if dir_value else None

def compute_fingerprint(source_content_hash: str, compiler_id: str, flags: list[str]) -> str:
    """소스 내용 해시 + 컴파일러 식별자 + 컴파일 플래그로 캐시 키 계산."""
    parts = [source_content_hash, compiler_id] + sorted(flags)
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

# ============================================================
# 오브젝트 파일 캐시 (C/C++ -- 단일 파일 하나 + 헤더 매니페스트)
# ============================================================

def try_fetch(
    backend: DirCacheBackend | HttpCacheBackend, fingerprint: str, obj_path: Path, project_root: Path
) -> dict[str, FileStat] | None:
    """원격 캐시에서 오브젝트 파일을 가져오기 시도. 헤더 불일치/캐시 없음/실패는 전부 None(미스)."""
    if isinstance(backend, HttpCacheBackend):
        obj_bytes = _http_get(backend, f"objects/{fingerprint}.o")
        headers_bytes = _http_get(backend, f"objects/{fingerprint}.headers.json")
    else:
        obj_bytes = _read_file(backend.path / f"{fingerprint}.o")
        headers_bytes = _read_file(backend.path / f"{fingerprint}.headers.json")

    if obj_bytes is None or headers_bytes is None:
        return None

    try:
        recorded_headers = json.loads(headers_bytes)
    except json.JSONDecodeError:
        return None

    header_stats: dict[str, FileStat] = {}
    for rel_path_str, recorded_hash in recorded_headers.items():
        header_path = project_root / rel_path_str
        if not header_path.exists():
            return None
        current_stat = get_file_stat(header_path)
        if current_stat.content_hash != recorded_hash:
            return None
        header_stats[str(header_path)] = current_stat

    try:
        obj_path.parent.mkdir(parents=True, exist_ok=True)
        obj_path.write_bytes(obj_bytes)
    except OSError:
        return None

    return header_stats

def store(
    backend: DirCacheBackend | HttpCacheBackend,
    fingerprint: str,
    obj_path: Path,
    header_stats: dict[str, FileStat],
    project_root: Path,
) -> None:
    """컴파일 성공 직후 오브젝트+헤더 해시를 원격 캐시에 업로드 (실패해도 조용히 무시)."""
    recorded_headers = {}
    for path_str, stat in header_stats.items():
        try:
            rel = str(Path(path_str).relative_to(project_root))
        except ValueError:
            continue  # 프로젝트 밖 헤더(시스템 헤더 등) -> 매니페스트에 안 남김
        recorded_headers[rel] = stat.content_hash
    headers_bytes = json.dumps(recorded_headers).encode("utf-8")

    try:
        obj_bytes = obj_path.read_bytes()
    except OSError:
        return

    if isinstance(backend, HttpCacheBackend):
        _http_put(backend, f"objects/{fingerprint}.o", obj_bytes)
        _http_put(backend, f"objects/{fingerprint}.headers.json", headers_bytes)
    else:
        _write_file_atomic(backend.path, f"{fingerprint}.o", obj_bytes)
        _write_file_atomic(backend.path, f"{fingerprint}.headers.json", headers_bytes)

# ============================================================
# 디렉토리 캐시 (Java classes_dir -- 여러 파일을 통째로)
# ============================================================

_DIR_CACHE_MARKER = ".stoke-cache-complete"

def try_fetch_dir(backend: DirCacheBackend | HttpCacheBackend, fingerprint: str, output_dir: Path) -> bool:
    """원격 캐시에서 디렉토리 전체(예: Java classes_dir)를 통째로 가져오기 시도. 성공 시 True."""
    if isinstance(backend, HttpCacheBackend):
        return _http_fetch_dir(backend, fingerprint, output_dir)
    return _dir_fetch_dir(backend.path, fingerprint, output_dir)

def store_dir(backend: DirCacheBackend | HttpCacheBackend, fingerprint: str, source_dir: Path) -> None:
    """빌드 성공 직후 디렉토리 전체를 원격 캐시에 업로드 (실패해도 조용히 무시)."""
    if isinstance(backend, HttpCacheBackend):
        _http_store_dir(backend, fingerprint, source_dir)
    else:
        _dir_store_dir(backend.path, fingerprint, source_dir)

# ============================================================
# DirCacheBackend 구현 (기존 디렉토리 공유 방식)
# ============================================================

def _read_file(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except OSError:
        return None

def _write_file_atomic(cache_dir: Path, name: str, data: bytes) -> None:
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        tmp = cache_dir / f"{name}.tmp-{os.getpid()}"
        tmp.write_bytes(data)
        tmp.replace(cache_dir / name)
    except OSError:
        pass

def _dir_fetch_dir(cache_dir: Path, fingerprint: str, output_dir: Path) -> bool:
    cached_dir = cache_dir / fingerprint
    marker = cached_dir / _DIR_CACHE_MARKER
    try:
        if not marker.exists():
            return False
        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.copytree(cached_dir, output_dir, ignore=shutil.ignore_patterns(_DIR_CACHE_MARKER))
        return True
    except OSError:
        return False

def _dir_store_dir(cache_dir: Path, fingerprint: str, source_dir: Path) -> None:
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        final_dir = cache_dir / fingerprint
        if (final_dir / _DIR_CACHE_MARKER).exists():
            return  # 이미 다른 머신/프로세스가 완전한 캐시를 올려둔 상태
        tmp_dir = cache_dir / f"{fingerprint}.tmp-{os.getpid()}"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        shutil.copytree(source_dir, tmp_dir)
        (tmp_dir / _DIR_CACHE_MARKER).touch()
        if final_dir.exists():
            shutil.rmtree(final_dir)
        tmp_dir.replace(final_dir)
    except OSError:
        pass

# ============================================================
# HttpCacheBackend 구현
# ============================================================

def _http_get(backend: HttpCacheBackend, path: str) -> bytes | None:
    req = urllib.request.Request(f"{backend.base_url}/{path}", headers=backend.headers)
    try:
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as response:
            return response.read()
    except Exception:
        return None  # 404/네트워크 오류/타임아웃/인증 실패 -- 전부 캐시 미스로 취급 (fail open)

def _http_put(backend: HttpCacheBackend, path: str, data: bytes) -> None:
    req = urllib.request.Request(
        f"{backend.base_url}/{path}", data=data, method="PUT",
        headers={**backend.headers, "Content-Type": "application/octet-stream"},
    )
    try:
        urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT)
    except Exception:
        pass  # 업로드 실패해도 로컬 빌드 결과는 이미 있으니 조용히 무시

def _http_fetch_dir(backend: HttpCacheBackend, fingerprint: str, output_dir: Path) -> bool:
    tar_bytes = _http_get(backend, f"dirs/{fingerprint}.tar")
    if tar_bytes is None:
        return False
    try:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
            for member in tf.getmembers():
                member_path = (output_dir / member.name).resolve()
                if not member_path.is_relative_to(output_dir.resolve()):
                    return False  # zip-slip 방지
            tf.extractall(output_dir)
        return True
    except (OSError, tarfile.TarError):
        return False

def _http_store_dir(backend: HttpCacheBackend, fingerprint: str, source_dir: Path) -> None:
    try:
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w") as tf:
            tf.add(source_dir, arcname=".")
        _http_put(backend, f"dirs/{fingerprint}.tar", buf.getvalue())
    except OSError:
        pass
