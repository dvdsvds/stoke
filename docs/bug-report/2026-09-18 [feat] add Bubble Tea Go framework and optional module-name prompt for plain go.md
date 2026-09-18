# Bubble Tea 프레임워크 스캐폴딩 추가 + plain go의 모듈명 프롬프트 개선

- 날짜: 2026-09-18
- 심각도: feat
- 상태: 완료

## 배경

"stoke에 gin 말고 TUI/CLI 전용 템플릿이 있나?"는 질문에서 시작. 확인해보니 Go 프레임워크 스캐폴딩(`src/stoke/languages/go/frameworks/`)엔 gin/echo/fiber/chi 네 개뿐이고 전부 웹 프레임워크라 TUI/CLI 전용 템플릿은 없었음. 이어서 "Bubble Tea는 프레임워크냐 라이브러리냐"는 질문에 답하면서(Cobra는 라이브러리에 가깝고, Bubble Tea는 Elm 아키텍처를 강제하는 IoC 구조라 프레임워크에 가깝다는 결론) Bubble Tea를 새 프레임워크로 추가하기로 함.

## 작업 내용

### 1. `src/stoke/languages/go/frameworks/bubbletea.py` 신규 작성

gin.py와 동일한 패턴(`cmd_init_bubbletea`):
- Go 모듈 이름 프롬프트 (`sanitize_go_module_name` 사용)
- `stoke.toml` 작성
- `main.go` 작성 — 커서로 항목 선택/체크하는 최소 Bubble Tea 예제 (Model-Update-View 골격)
- `go mod init` → `go get github.com/charmbracelet/bubbletea` → `go mod tidy` (아래 별도 버그 참고)

### 2. CLI 등록

`src/stoke/cli/__init__.py:44,78` — import 및 `_INIT_FRAMEWORK_HANDLERS["bubbletea"]` 추가. `stoke init bubbletea`로 바로 실행 가능.

### 3. 문서 갱신

프레임워크 목록에 Bubble Tea 추가: `README.md`(요약 문단 + 기능 bullet), `docs/README_ko.md`(기능 bullet + 프레임워크 표), `docs/HOW_TO_USE.md`, `docs/HOW_TO_USE_KO.md`.

### 4. plain go(`stoke init`, 프레임워크 미지정)의 모듈명 정책 개선

**처음엔 버그로 의심**: `stoke init gin`은 "Go module name" 프롬프트를 물어보는데 `stoke init go`(대화형, 프레임워크 없이)는 안 물어보고 그냥 `project_name`을 모듈명으로 씀. 검토 결과 실제로는 버그가 아니라 정책 차이였음 — gin은 외부 패키지를 import하니 실제 모듈 경로가 필요하지만, plain go는 로컬 전용 최소 스캐폴드를 가정한 합리적 기본값. 다만 GitHub 등에 올라갈 수도 있는 프로젝트를 고려해서, "published 여부"에 따라 분기하도록 개선하기로 함:

- `src/stoke/languages/go/init.py`: `_select_go_module_name(project_name)` 추가. "Will this be published (e.g. on GitHub)?" (기본값 no)를 물어보고, yes면 gin과 동일하게 module name 프롬프트 + `sanitize_go_module_name`, no면 기존처럼 `project_name` 그대로 반환.
- `_write_example_go(project_root, project_name, module_name=None)` — `module_name` 파라미터 추가(없으면 `project_name`으로 폴백), `go mod init`에 이걸 사용.
- `src/stoke/init.py:35,200,241` — 대화형 `cmd_init()`의 go 분기에서 `_select_go_module_name` 호출 후 `_write_example_go`에 전달.
- 비대화형 경로(`stoke init --language=go --yes`)는 원래부터 프롬프트가 없는 흐름이라 그대로 유지 — `project_name`을 모듈명으로 그대로 씀 (`src/stoke/init.py:355`, 변경 없음).

## 관련 발견 (별도 문서)

- Bubble Tea 스캐폴딩 검증 중 `go.mod`에서 직접 import하는 패키지 자체가 `// indirect`로 잘못 표시되는 버그 발견/수정 → [2026-09-18 [bug][medium] go mod tidy missing after go get in Go framework scaffolds.md](<2026-09-18 [bug][medium] go mod tidy missing after go get in Go framework scaffolds.md>)
- 프로젝트 로컬 전용 툴체인(`.stoke/toolchains/`)이 사용자 셸 PATH에 없어서 `go mod tidy`를 손으로 못 돌리는 문제 발견 → [2026-09-18 [design] project-local toolchains unreachable from user shell.md](<2026-09-18 [design] project-local toolchains unreachable from user shell.md>)
- 같은 조사 도중 JS/TS `stoke add`/`stoke remove`에서 발견한 별개의 PATH 관련 버그 → [2026-09-18 [bug][high] stoke add-remove for JS-TS ignores project-local Node toolchain.md](<2026-09-18 [bug][high] stoke add-remove for JS-TS ignores project-local Node toolchain.md>)
