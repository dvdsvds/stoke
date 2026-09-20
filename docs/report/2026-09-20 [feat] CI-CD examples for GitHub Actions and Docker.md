# CI/CD 예제: GitHub Actions + Docker

- 날짜: 2026-09-20
- 종류: feat

## 배경

"CI/CD(GitHub Actions, Docker) 연동이 어렵다"는 외부 지적. 실제로는 stoke가 Python 내장 단일 실행 파일로 배포되고, `stoke init --language=X --yes` 같은 비대화형 초기화도 이미 있어서 구조적으로 막혀 있진 않았음 — 근데 이걸 보여주는 예제/가이드가 하나도 없었음.

## 변경

- `docs/ci/github-actions.yml` 신규: stoke release tarball 설치 → `actions/cache`로 공유 빌드 캐시(`STOKE_REMOTE_CACHE_DIR`) 복원 → `stoke build`/`stoke test`/`stoke audit` 실행. `stoke audit`는 CVE 발견 시 non-zero exit이라 그대로 머지 게이트로 씀.
- `docs/ci/Dockerfile` 신규: 멀티스테이지 빌드 예제 (Go 타겟 기준). build 스테이지에서 `stoke install <language> --version=X` + `stoke build --release`, 런타임 이미지에는 `.stoke/<language>/<target>/<binary>` 산출물만 복사.
- `docs/HOW_TO_USE.md`/`_KO.md`에 "6.6 CI/CD" 섹션 추가, 위 두 예제 링크.
- `README.md`/`docs/README_ko.md`/`docs/FEATURES.md`/`.ko.md`에 CI/CD 예제 링크 및 "단일 바이너리라 런타임 사전 설치 불필요" 설명 추가.

## 검증

`docs/ci/github-actions.yml`을 PyYAML로 파싱해 문법 확인. Dockerfile 내 경로(`.stoke/go/myapp/myapp`)는 `go/adapter.py`의 `output_path` 정의(`.stoke/go/<target>/<target-name>`)로 실제 코드 확인 후 작성 — 이전에 `dist/`로 잘못 가정했던 초안을 코드 확인 후 수정함. `stoke install`이 비대화형(프롬프트 없음)인 것도 `install_lang.py`에서 확인.

## 적용 안 한 것

- Jenkins나 다른 CI 시스템 예제 — GitHub Actions만 먼저 커버.
