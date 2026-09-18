"""공유 디렉토리(STOKE_REMOTE_CACHE_DIR) 기반 원격/공유 빌드 캐시, 헤더까지 content-hash로 검증."""
import hashlib
import json
import os
import shutil
from pathlib import Path

from stoke.cache import get_file_stat, FileStat

def get_remote_cache_dir() -> Path | None:
    """공유 캐시 디렉토리 (STOKE_REMOTE_CACHE_DIR 환경변수, 안 정해져 있으면 None)."""
    value = os.environ.get("STOKE_REMOTE_CACHE_DIR")
    return Path(value) if value else None

def compute_fingerprint(source_content_hash: str, compiler_id: str, flags: list[str]) -> str:
    """소스 내용 해시 + 컴파일러 식별자 + 컴파일 플래그로 캐시 키 계산."""
    parts = [source_content_hash, compiler_id] + sorted(flags)
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

def try_fetch(
    cache_dir: Path, fingerprint: str, obj_path: Path, project_root: Path
) -> dict[str, FileStat] | None:
    """원격 캐시에서 오브젝트 파일을 가져오기 시도. 헤더 불일치/캐시 없음/실패는 전부 None(미스)."""
    obj_cache_path = cache_dir / f"{fingerprint}.o"
    headers_cache_path = cache_dir / f"{fingerprint}.headers.json"

    try:
        if not obj_cache_path.exists() or not headers_cache_path.exists():
            return None
        recorded_headers = json.loads(headers_cache_path.read_text(encoding="utf-8"))
    except OSError:
        return None
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
        shutil.copyfile(obj_cache_path, obj_path)
    except OSError:
        return None

    return header_stats

def store(
    cache_dir: Path,
    fingerprint: str,
    obj_path: Path,
    header_stats: dict[str, FileStat],
    project_root: Path,
) -> None:
    """컴파일 성공 직후 오브젝트+헤더 해시를 원격 캐시에 업로드 (실패해도 조용히 무시, 원자적 rename)."""
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)

        obj_cache_path = cache_dir / f"{fingerprint}.o"
        tmp_obj = cache_dir / f"{fingerprint}.o.tmp-{os.getpid()}"
        shutil.copyfile(obj_path, tmp_obj)
        tmp_obj.replace(obj_cache_path)

        recorded_headers = {}
        for path_str, stat in header_stats.items():
            try:
                rel = str(Path(path_str).relative_to(project_root))
            except ValueError:
                continue  # 프로젝트 밖 헤더(시스템 헤더 등) -> 매니페스트에 안 남김
            recorded_headers[rel] = stat.content_hash

        headers_cache_path = cache_dir / f"{fingerprint}.headers.json"
        tmp_headers = cache_dir / f"{fingerprint}.headers.json.tmp-{os.getpid()}"
        tmp_headers.write_text(json.dumps(recorded_headers), encoding="utf-8")
        tmp_headers.replace(headers_cache_path)
    except OSError:
        pass

_DIR_CACHE_MARKER = ".stoke-cache-complete"

def try_fetch_dir(cache_dir: Path, fingerprint: str, output_dir: Path) -> bool:
    """원격 캐시에서 디렉토리 전체(예: Java classes_dir)를 통째로 가져오기 시도. 성공 시 True."""
    cached_dir = cache_dir / fingerprint
    marker = cached_dir / _DIR_CACHE_MARKER
    try:
        if not marker.exists():
            return False
        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.copytree(
            cached_dir, output_dir, ignore=shutil.ignore_patterns(_DIR_CACHE_MARKER)
        )
        return True
    except OSError:
        return False

def store_dir(cache_dir: Path, fingerprint: str, source_dir: Path) -> None:
    """빌드 성공 직후 디렉토리 전체를 원격 캐시에 업로드 (임시 이름 복사 후 rename, 마커로 완료 표시)."""
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
