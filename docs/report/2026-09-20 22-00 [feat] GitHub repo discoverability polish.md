# GitHub 저장소 검색/신뢰도 개선

- 날짜: 2026-09-20
- 종류: feat

## 배경

Threads에 릴리스 소식을 올리고 나서, "이제 사람들이 실제로 쓰게 하려면 저장소를 어떻게 꾸며야 할지" 논의. `gh repo view`로 실제 상태를 확인해서 근거 있는 항목만 고침.

## 발견한 것

- **토픽에 오타**: `bulid-tool` (build-tool이어야 함) — GitHub 검색에서 "build-tool"로 찾는 사람들한테 아예 안 걸림.
- 토픽이 python/java/cpp 등 일부 언어 + django/fastapi/flask/spring-boot 프레임워크 위주였고, 실제로 지원하는 go/rust/kotlin/csharp/ruby/php/javascript/typescript나 이번에 추가된 기능(monorepo, sbom, supply-chain-security)은 하나도 없었음.
- README에 배지가 하나도 없었음 — MIT 라이선스인데 배지로 안 보여줌, 릴리스 버전/빌드 상태도 안 보임.
- `CONTRIBUTING.md`, 이슈 템플릿 전무.

## 변경

- **토픽 정리** (`gh repo edit`): `bulid-tool` 삭제하고 `build-tool`로, django/fastapi/flask/spring-boot(개별 프레임워크라 상대적으로 덜 검색됨) 빼고 go/rust/kotlin/csharp/ruby/php/javascript/typescript/monorepo/sbom/supply-chain-security/cli 추가. GitHub 토픽은 저장소당 20개 제한이 있어서(테스트해보다가 발견) 그 안에서 우선순위 조정.
- **README.md에 배지 4개 추가**: 최신 릴리스 버전, 빌드 상태(release.yml 워크플로우), 라이선스, 다운로드 수 (전부 shields.io, 실제로 4개 URL 다 curl로 200 확인).
- **`CONTRIBUTING.md` 신규**: 버그 리포트/기능 요청 시 뭘 적어야 하는지, 개발 환경 세팅(`pip install -e .`), 플러그인 시스템으로 언어/프레임워크 추가하는 법, PR 가이드라인, `docs/report/` 관례 소개.
- **`.github/ISSUE_TEMPLATE/`**: bug_report.md, feature_request.md 신규.

## 검증

- `gh repo view`로 토픽 최종 상태(19개, 오타 없음) 확인.
- 배지 URL 4개 전부 `curl -o /dev/null -w "%{http_code}"`로 200 확인.
- 워크플로우 파일명(`release.yml`)이 빌드 상태 배지 URL과 정확히 일치하는지 `.github/workflows/` 실제 파일 목록으로 확인.

## 적용 안 한 것

- README 맨 위 데모 GIF/터미널 녹화 -- 효과는 제일 클 것 같지만 제작 자체가 별도 작업이라 이번 범위에선 보류.
- og:image(소셜 공유 미리보기 이미지) 설정 여부 확인 -- 아직 안 함.
- "왜 stoke인가" 비교 표(vs Maven/Gradle/npm 스크립트) -- 콘텐츠 작성이 필요해서 보류.
