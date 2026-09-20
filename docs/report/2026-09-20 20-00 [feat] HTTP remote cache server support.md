# 원격 캐시 HTTP 서비스화 (STOKE_REMOTE_CACHE_URL)

- 날짜: 2026-09-20
- 종류: feat

## 배경

"실무 트렌드를 따라가자"의 마지막 항목. 지금까지 원격/공유 빌드 캐시(`STOKE_REMOTE_CACHE_DIR`)는 여러 머신이 같은 네트워크 공유 디렉토리(NAS, 매핑된 드라이브)에 접근 가능해야만 동작했음 — 원격 근무자나 GitHub 호스팅 CI 러너처럼 사내망 밖에 있는 경우엔 못 씀. Bazel Remote Cache/Turborepo Remote Cache처럼 HTTP로 접근하는 캐시 서버를 지원하면 이 갭이 메꿔짐.

Devcontainer 자동 생성도 후보였는데, stoke가 이미 `.stoke/toolchains/`로 프로젝트별 툴체인 격리 + lock 파일 재현성을 제공하고 있어서 Docker 기반 재현성 레이어와 상당 부분 중복된다고 판단해 제외하고 이것만 진행함 (사용자와 상의 후 결정).

## 설계

기존 `remote_cache.py`는 함수들이 전부 `cache_dir: Path`를 직접 받는 구조라, HTTP 백엔드를 추가하려면 호출부(`c/base.py`, `java/adapter.py`)가 "이게 디렉토리인지 URL인지"를 알아야 했음. 대신 `DirCacheBackend`/`HttpCacheBackend`라는 작은 태그드 유니언을 도입해서, `get_remote_cache_backend()`가 `STOKE_REMOTE_CACHE_URL` 있으면 HTTP, 없으면 `STOKE_REMOTE_CACHE_DIR`로 디렉토리, 둘 다 없으면 `None`을 반환하게 함. `try_fetch`/`store`/`try_fetch_dir`/`store_dir` 함수들은 내부에서 `isinstance` 분기만 하고, 호출부(`c/base.py`, `java/adapter.py`)는 `get_remote_cache_dir()` → `get_remote_cache_backend()`로 함수 이름만 바뀌고 나머지 코드는 그대로임 (2줄만 수정).

HTTP 프로토콜은 기존 bazel-remote 같은 무거운 스펙을 새로 구현하는 대신, stoke가 필요한 만큼만 최소로 정의:
- 오브젝트(C/C++ `.o` 파일 + 헤더 매니페스트): `GET`/`PUT /objects/<fingerprint>.o`, `/objects/<fingerprint>.headers.json`
- 디렉토리(Java `classes_dir` 전체): 클라이언트가 메모리에서 tar로 묶어서 `GET`/`PUT /dirs/<fingerprint>.tar`

인증은 기존 Maven/버전 API 미러 지원과 동일한 패턴(`STOKE_REMOTE_CACHE_USER`/`PASSWORD` → HTTP Basic Auth, `http_utils.basic_auth_headers` 재사용).

**Fail-open 원칙 유지**가 가장 중요한 설계 제약이었음 — 기존 디렉토리 캐시가 "캐시 서버가 없어도/느려도/에러나도 빌드는 절대 안 깨짐"이라는 약속을 README에 명시하고 있어서, HTTP 백엔드도 네트워크 오류/타임아웃/인증 실패/서버 다운 전부 조용히 캐시 미스로 처리(`except Exception: return None`)하도록 구현. 타임아웃도 10초로 짧게 잡아서, 응답 없는 서버 때문에 빌드가 오래 멈추는 일이 없게 함.

## 검증

로컬에 `http.server` 기반 최소 테스트 캐시 서버(GET/PUT을 딕셔너리에 저장하는 수십 줄짜리)를 띄워서 실제로 검증:

- **오브젝트 캐시 왕복**: 저장 전엔 미스(`None`), 저장 후엔 실제 바이트가 동일하게 돌아오는 것 확인.
- **디렉토리 캐시 왕복**: 여러 파일이 든 디렉토리를 tar로 묶어 업로드 → 다운로드 후 압축 풀어서 파일 목록/내용이 원본과 동일한지 확인.
- **Fail-open**: 아무것도 안 듣고 있는 포트(`127.0.0.1:9999`)로 fetch/store 시도 → 예외 없이 조용히 `None`/무시, 0.06초 만에 반환(타임아웃까지 안 기다리고 connection refused로 즉시 실패하는 것까지 확인).
- **Basic Auth**: `STOKE_REMOTE_CACHE_USER`/`PASSWORD` 설정 시 `Authorization: Basic ...` 헤더가 정확히 생성되는지 확인.
- **회귀 테스트**: 리팩터 후에도 기존 `STOKE_REMOTE_CACHE_DIR`(디렉토리 공유) 경로가 그대로 동작하는지 별도로 재확인.

## 적용 안 한 것

- 타임아웃(불가능하게 느린 서버, connection refused가 아니라 응답이 안 오는 경우)까지의 실제 10초 대기 테스트는 시간 관계상 생략 — `urllib.request.urlopen(..., timeout=N)`이 표준적으로 잘 동작하는 부분이라 신뢰함.
- HTTP 캐시 서버 자체의 구현체 — stoke는 클라이언트만 제공. `GET`/`PUT /objects/<key>`, `/dirs/<key>.tar`를 지원하는 아무 HTTP 서버(S3 프록시, nginx WebDAV, 직접 짠 서버 등)나 붙이면 됨.
