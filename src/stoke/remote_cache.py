"""
공유 디렉토리 기반 원격/공유 빌드 캐시.

STOKE_REMOTE_CACHE_DIR 환경변수로 네트워크 드라이브나 NAS 같은, 여러 머신이
접근 가능한 디렉토리를 지정하면 팀/CI 전체가 컴파일 결과물을 공유함 — 한 머신이
컴파일한 오브젝트 파일을 다른 머신이 재컴파일 없이 그대로 받아 씀.

캐시 키(fingerprint)는 소스 파일 내용 해시 + 컴파일러 식별자 + 컴파일 플래그로 계산.
헤더 의존성은 컴파일 전에는 알 수 없으므로, 캐시에 오브젝트 파일과 함께 "이 오브젝트를
만들 때 실제로 included된 헤더들과 그 내용 해시" 목록을 같이 저장해두고, 다음에 같은
fingerprint를 조회할 때 그 헤더들이 로컬에서도 내용까지 동일한지 검증한 뒤에만 히트로
인정함 (stoke.cache의 content-hash 기반 무효화와 동일한 원리).
"""
import hashlib
import json
import os
import shutil
from pathlib import Path

from stoke.cache import get_file_stat, FileStat

def get_remote_cache_dir() -> Path | None:
    """
    공유 캐시 디렉토리. STOKE_REMOTE_CACHE_DIR 환경변수로 설정.
    안 정해져 있으면 None — 원격 캐시 비활성화, 기존 로컬 전용 동작과 완전히 동일.
    """
    value = os.environ.get("STOKE_REMOTE_CACHE_DIR")
    return Path(value) if value else None

def compute_fingerprint(source_content_hash: str, compiler_id: str, flags: list[str]) -> str:
    """
    소스 내용 해시 + 컴파일러 식별자 + 컴파일 플래그로 캐시 키 계산.
    이 조합이 같으면 어느 머신에서 컴파일했든 동일한 오브젝트가 나온다는 전제
    (실제로는 아래 헤더 검증까지 통과해야 최종 히트로 인정).
    """
    parts = [source_content_hash, compiler_id] + sorted(flags)
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

def try_fetch(
    cache_dir: Path, fingerprint: str, obj_path: Path, project_root: Path
) -> dict[str, FileStat] | None:
    """
    원격 캐시에서 오브젝트 파일을 가져오기 시도.

    헤더 경로는 project_root 기준 상대경로로 매니페스트에 기록돼 있음 (절대경로를
    그대로 쓰면 다른 머신/다른 체크아웃 경로에서는 절대 안 맞거나, 최악의 경우
    우연히 그 절대경로에 있는 *다른* 파일을 검증해버리는 사고가 남 — 실제로 이걸
    절대경로로 했다가 로컬 테스트에서 다른 프로젝트 폴더의 헤더를 잘못 검증하는
    버그를 재현한 뒤 이 방식으로 고침). 프로젝트 밖 헤더(시스템 헤더 등)는 매니페스트에
    안 남기고, 대신 fingerprint에 이미 들어있는 compiler_id(툴체인 식별자)가 그 역할을 함.

    반환:
    - 히트(오브젝트 존재 + 기록된 헤더 전부가 로컬에서도 내용까지 동일):
      obj_path에 복사하고, {헤더 절대경로: FileStat} 반환 (호출부가 로컬 캐시에 그대로 기록 가능).
    - 미스(캐시 없음/손상/헤더 불일치/복사 실패 등): None.
      네트워크 문제로 원격 캐시에 접근이 안 되는 경우도 그냥 미스로 처리하고
      로컬 컴파일로 자연스럽게 넘어감 — 원격 캐시는 있으면 빠른 최적화일 뿐,
      없다고 빌드 자체가 실패해선 안 됨.
    """
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
    """
    컴파일 성공 직후, 오브젝트 파일 + 헤더 해시 목록을 원격 캐시에 업로드.
    실패해도(네트워크 끊김, 권한 문제 등) 이미 로컬 빌드는 성공한 상태이므로
    조용히 무시 — 원격 캐시 쓰기 실패가 빌드 실패로 이어지면 안 됨.

    header_stats의 키(절대경로)는 project_root 기준 상대경로로 변환해서 저장함
    (다른 머신에서도 검증 가능하려면 이 프로젝트 안에서의 상대 위치만 의미가 있음).
    project_root 밖의 헤더(시스템 헤더 등)는 상대경로로 못 만드니 매니페스트에서 제외 —
    fingerprint에 이미 포함된 compiler_id가 툴체인/시스템 헤더 차이를 대신 잡아줌.

    임시 파일에 먼저 쓰고 rename하는 이유: 여러 머신/프로세스가 동시에 같은
    fingerprint로 쓰기를 시도해도, 다른 쪽이 절반만 쓰인 파일을 읽는 일이 없게 하기 위함
    (같은 파일시스템 안에서의 rename은 원자적).
    """
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
    """
    원격 캐시에서 디렉토리 전체(예: Java의 classes_dir)를 통째로 가져오기 시도.

    C/C++ 쪽 오브젝트 캐시(try_fetch)와 다른 점: 파일 단위 헤더 검증이 없음. 대신
    fingerprint 자체가 "이 디렉토리를 만들어낸 소스 파일 전체 세트의 내용"을
    통째로 반영하도록 호출부에서 계산해야 함 (languages/java/adapter.py 참고) —
    소스 파일 하나라도 내용이 바뀌면 fingerprint가 통째로 달라지므로, 부분 검증이
    필요 없음. 대신 캐시 단위가 파일이 아니라 타겟 전체라 세밀함은 떨어짐.

    성공 시 output_dir을 캐시 내용으로 완전히 교체하고 True.
    실패(캐시 없음/불완전/복사 실패)시 output_dir은 안 건드리고 False.
    """
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
    """
    빌드 성공 직후, 디렉토리 전체(예: classes_dir)를 원격 캐시에 업로드.
    실패해도 이미 로컬 빌드는 성공했으니 조용히 무시.

    임시 이름으로 먼저 복사한 뒤 최종 이름으로 rename — 여러 머신/프로세스가
    동시에 같은 fingerprint에 쓰더라도 절반만 복사된 상태를 다른 쪽이 못 보게 함.
    완료 표시로 마커 파일을 맨 마지막에 남김: rename 도중 프로세스가 죽어도
    (또는 다른 프로세스가 먼저 같은 이름으로 rename을 마쳐서 대상 디렉토리가 이미
    있어도) 마커 없는 캐시 디렉토리는 그냥 미스로 처리되도록.
    """
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
