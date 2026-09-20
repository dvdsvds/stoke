# 네트워크 조회 병렬화 + cache-server 업로드 스트리밍

- 날짜: 2026-09-21
- 종류: perf

## 배경

"남은 기능이 있나?" 목록에서 사용자가 선택한 두 항목:
1. `stoke audit`/`stoke outdated`의 네트워크 조회가 직렬(순차) — 취약점/패키지 많으면 느림.
2. `stoke cache-server`가 업로드 본문 전체를 `self.rfile.read(length)`로 메모리에 통째로 올림 — 동시 다중 업로드 시 메모리 부담.

## 변경

### 1. `src/stoke/osv.py`
- `_fetch_summaries(ids, timeout)`가 `for vid in ids:` 직렬 루프였던 걸 `ThreadPoolExecutor(max_workers=min(8, len(ids)))`로 병렬화.
- 각 조회는 이미 `except Exception: summaries[vid] = None`으로 개별 실패를 흡수하는 구조라 병렬화해도 새로운 실패 모드가 생기지 않음.

### 2. `src/stoke/cli/outdated.py`
- `_collect_outdated(names_and_versions, latest_lookup)`도 동일하게 `ThreadPoolExecutor`로 병렬화. `pypi_latest`/`maven_latest` 각각 독립적인 HTTP 조회라 순서 보장 불필요 -- `zip(items, latests)`로 매핑만 유지.

### 3. `src/stoke/remote_cache.py`
- `stream_to_atomic_tmp(cache_dir, name, stream, length, chunk_size=1MB)` 추가 -- 스트림에서 청크 단위로 읽어 임시 파일에 쓰고, 그 임시 파일 경로를 반환 (rename은 호출자 책임 -- write-once 검사처럼 rename 직전에 호출자가 추가로 확인해야 하는 경우가 있어서).
- 기존 `_write_file_atomic`의 임시 파일 이름 생성 부분을 `_atomic_tmp_path`로 뽑아서 공유. 기존엔 `os.getpid()`만 썼는데, `cache_server.py`가 스레딩 서버라 같은 프로세스 안 여러 스레드가 충돌할 여지가 있어서 `threading.get_ident()`도 섞음.

### 4. `src/stoke/cache_server.py`
- `do_PUT`이 `data = self.rfile.read(length)`로 본문 전체를 메모리에 올린 뒤 tmp 파일에 쓰던 걸, `stream_to_atomic_tmp`로 바꿔서 청크 단위 스트리밍으로 변경.
- tmp-write-then-replace 로직 자체를 `remote_cache.py`의 공유 헬퍼로 대체 -- 코드 중복 제거.

## 검증

- `_collect_outdated`를 네트워크 없이 mock lookup 함수로 단위 테스트 -- 동시 호출 시에도 이름-값 매핑이 정확히 유지되는 것 확인.
- 실제 cache-server를 백그라운드 스레드로 띄워서:
  - 5MB 페이로드로 PUT (청크 스트리밍 경로 실제로 타는 크기) -- 200 OK.
  - 같은 키로 재 PUT -- write-once 규칙대로 409 Conflict.
  - GET으로 읽어와서 바이트 단위로 원본과 일치 확인 (5,242,880 bytes 일치).
  - 캐시 디렉토리에 `.tmp-` 접미사 잔여 파일 없음 (성공/실패 경로 모두 정리됨) 확인.
- 실제 OSV.dev API로 `query_batch("PyPI", {"django": "2.0.0", "requests": "2.20.0", "flask": "0.12"})` 호출 -- django 32건, requests 8건, flask 8건, 총 48개 취약점 summary를 3.10초에 조회 완료 (이전 직렬 방식이면 48번의 왕복 지연이 그대로 누적됐을 구간).

## 적용 안 한 것

- `stoke audit`의 querybatch 자체(1차 배치 조회)는 이미 단일 요청이라 병렬화 대상이 아님 -- 병렬화는 `_fetch_summaries`(2차 개별 조회)에만 해당.
- ThreadPoolExecutor worker 수(8)는 하드코딩 -- 환경변수로 조정 가능하게 만드는 건 실제로 필요하다는 신호가 있을 때.
- cache-server의 다운로드(GET) 경로는 여전히 `path.read_bytes()`로 전체를 메모리에 올림 -- 업로드와 달리 다운로드는 클라이언트가 이미 Content-Length를 알고 받는 구조라 상대적으로 급하지 않다고 판단, 이번엔 범위 밖.
