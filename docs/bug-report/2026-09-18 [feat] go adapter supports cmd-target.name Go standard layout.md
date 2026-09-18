# Go 어댑터가 `cmd/<target.name>/` 표준 레이아웃을 못 찾던 문제

- 날짜: 2026-09-18
- 심각도: feat (기능 누락에 가까움 — `_package_path()`의 기존 docstring이 지원한다고 잘못 적혀 있었음)
- 상태: 수정됨

## 배경

carty 프로젝트에서 `stoke.toml`의 `[targets.carty]`에 경로 지정 필드가 없어서 stoke가 빌드 대상을 루트(`.`)로 잡는 걸 발견. 조사 결과 stoke.toml에는애초에 Go용 `path`/`main` 필드 자체가 없고(`Target` 데이터클래스의 `source_dir`는 C/C++ cmake/meson 전용), Go 빌드 경로는 순전히 `GoAdapter._package_path()`의 폴더 구조 관례로만 정해짐을 확인.

그런데 그 관례를 보니 `<target.name>/` 서브디렉토리만 확인하고 있었고, 정작 함수 docstring에는 "go.mod 하나 밑에 cmd/api, cmd/worker처럼 여러 main 패키지를 두는 Go의 표준 관례를 그대로 씀"이라고 적혀 있었음 — 실제 Go 커뮤니티 표준 레이아웃은 `cmd/<name>/main.go`인데, 코드는 `<name>/main.go`(cmd/ 없이)만 지원해서 문서와 구현이 안 맞았음. `cmd/carty/main.go` 구조로 프로젝트를 짜면 stoke가 못 찾고 그냥 루트로 폴백했을 것.

## 수정

`src/stoke/languages/go/adapter.py`의 `_package_path()`에 우선순위 폴백 추가:

1. `cmd/<target.name>/`에 `.go` 파일이 있으면 `./cmd/<target.name>` (Go 표준 레이아웃, 신규)
2. 없으면 `<target.name>/`에 `.go` 파일이 있으면 `./<target.name>` (기존 stoke 관례, 유지)
3. 둘 다 없으면 `.`(프로젝트 루트, 기존 단일 타겟 프로젝트 — gin/echo/fiber/chi/bubbletea 스캐폴딩 전부 여기 해당)

## 검증

임시 디렉토리에 세 가지 레이아웃(`cmd/carty/main.go`, `other_target/main.go`, 아무것도 없음)을 만들어서 `GoAdapter._package_path()`를 직접 호출, 각각 `./cmd/carty`, `./other_target`, `.`로 정확히 갈리는 것 확인. 기존 동작(2번, 3번 케이스)이 안 깨지는 것도 같이 확인.

## 참고

프레임워크 스캐폴딩(gin 등)이 `cmd/` 레이아웃으로 생성하도록 바꾸는 건 별개 논의 — 이번엔 어댑터가 이미 존재하는 `cmd/` 레이아웃 프로젝트를 인식 못 하는 문제만 고침. 스캐폴딩 자체를 `cmd/<project>/main.go` 구조로 바꿀지는 아직 결정 안 함.
