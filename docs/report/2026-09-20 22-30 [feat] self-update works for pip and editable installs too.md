# stoke self-update: pip / pip install -e 설치도 지원

- 날짜: 2026-09-20
- 종류: feat

## 배경

기존 `stoke self-update`는 PyInstaller 단일 실행 파일 배포판에서만 동작하고, 그 외(소스 실행, `pip install -e .`)는 전부 거부했음. "설치 방식 상관없이 업데이트되게 하자"는 요청으로 확장.

## 설계

`importlib.metadata`로 현재 설치 방식을 실제로 판별함:

- **frozen**: `sys.frozen` -- 기존 로직 그대로 (바이너리 디렉토리 원자적 교체 / Windows 인스톨러).
- **editable** (`pip install -e .`, 즉 git 체크아웃 그 자체): `importlib.metadata.distribution("stoke-build").read_text("direct_url.json")`를 읽으면 `{"dir_info": {"editable": true}, "url": "file:///path/to/checkout"}` 형태로 정확히 어느 디렉토리가 소스인지 나옴. 이 값은 pip이 설치 시점에 기록해두는 표준 메타데이터라(PEP 610), stoke가 따로 추적할 필요 없이 pip한테 물어보면 됨. 이 디렉토리에서 `git status --porcelain`으로 워킹트리가 깨끗한지 확인 후 `git pull` -- **워킹트리에 커밋 안 된 변경사항 있으면 거부**(강제로 덮어쓰지 않음).
- **pip** (일반 `pip install`): stoke가 PyPI에 안 올라가 있어서(확인됨), `pip install --upgrade "stoke-build @ git+https://github.com/dvdsvds/stoke.git@v{latest}"`로 해당 릴리스 태그를 직접 가리켜서 재설치.
- **unknown**: 위 셋 다 아니면(예: 메타데이터 자체가 없는 이상한 설치) 명확히 에러 내고 릴리스 페이지 링크 안내.

## 변경

`src/stoke/self_update.py`:
- `detect_install_method()` -- "frozen"/"editable"/"pip"/"unknown" 반환.
- `_editable_source_dir()` -- PEP 610 `direct_url.json` 파싱.
- `update_editable_install()` -- 워킹트리 검사 + `git pull`.
- `update_pip_install(version)` -- GitHub 태그 가리켜서 `pip install --upgrade`.

`src/stoke/cli/self_update.py`: `cmd_self_update()`가 `detect_install_method()`로 분기해서 세 가지 업데이트 경로 중 하나를 실행하도록 재구성.

## 검증

이 세션 자체가 `pip install -e .`로 설치된 환경이라(`importlib.metadata`로 실제 확인함: `direct_url.json`이 정확히 이 저장소 경로를 가리킴), `detect_install_method()`가 "editable"을 정확히 반환하는 것부터 실제로 확인.

**진짜 업데이트 동작 검증**: 격리된 테스트용 클론을 만들어서(`/tmp`, 별도 venv로 `pip install -e .`) v2.4.1로 체크아웃해두고, `update_editable_install()`을 실제로 호출 → `git pull`이 실행되면서 실제로 v2.4.1 → v2.5.0으로 정상 업그레이드되는 것 확인 (버전 문자열로 직접 확인).

**안전장치 검증**: 같은 테스트 클론에 커밋 안 된 변경사항을 만들어두고 다시 호출 → "Uncommitted changes ... commit or stash them first"로 정확히 거부하는 것 확인 (강제로 덮어쓰지 않음).

## 적용 안 한 것

- `pip` 방식(일반 설치, editable 아님)의 실제 업그레이드는 로컬에서 재현하기 애매해서(애초에 PyPI에 없어서 `pip install stoke-build`가 안 됨, git URL 설치만 가능) 코드 리뷰 수준으로만 확인, 실제 실행 검증은 못 함.
- pipx로 설치된 경우 별도 처리 -- pipx도 내부적으로 pip을 쓰는 venv라 `sys.executable -m pip install --upgrade`가 그 pipx venv 안의 pip을 정확히 가리키긴 하지만, pipx 특유의 동작(예: `pipx upgrade`가 더 적절한 경우)까지는 고려 안 함.
