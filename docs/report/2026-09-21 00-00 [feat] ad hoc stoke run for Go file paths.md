# 즉석(ad hoc) `stoke run <go 파일 경로>` 지원

- 날짜: 2026-09-21
- 종류: feat

## 배경

실제 사용자(다른 프로젝트, `carty`)가 실사용 중에 겪은 문제: `stoke run cmd/colorpicker-preview/main.go`를 실행했더니 "target 'cmd/colorpicker-preview/main.go' not found in stoke.toml"로 에러남. `stoke run [target] [entry_file]`의 첫 번째 위치 인자가 파일 경로가 아니라 stoke.toml에 선언된 **타겟 이름**으로 해석되기 때문이었음. Go는 애초에 `entry_file` 오버라이드도 지원 안 함(`_ENTRY_OVERRIDABLE_LANGUAGES`가 python/js/ts/ruby/php만 포함).

기존에 있던 임시 우회법(타겟 이름을 `cmd/<이름>/`에 매핑하는 기존 관례를 이용해서 `[targets.colorpicker-preview]`를 stoke.toml에 미리 선언)은 여전히 유효하지만, 사용자 입장에선 "파일 경로를 줬는데 왜 안 되지"가 당연한 기대였음.

## 설계 논의

사용자가 먼저 우려한 부분: "cmd 밑에 파일이 여러 개면 main()을 찾아야 하는 거 아니냐, 그러면 느리지 않냐"는 질문이 있었는데 — **파일 스캔이 아예 필요 없다는 게 핵심**. Go는 파일 단위가 아니라 **디렉토리(패키지) 단위**로 컴파일되고, 패키지 안에 `main()`이 정확히 하나 있는지 검사하는 건 **Go 컴파일러의 일**임. stoke는 그냥 "이 파일이 들어있는 디렉토리"를 `go run`에 넘겨주기만 하면 됨 — 파일 내용을 열어보거나 다른 파일들을 뒤질 필요가 전혀 없어서, 스캔 비용 자체가 안 생김.

이미 있던 C/C++ ad-hoc 기능(`_find_adhoc_cpp_entry`, `stoke run sim`처럼 `src/sim.cpp`를 파일명 매칭으로 즉석 빌드)과 같은 자리(`cmd_run`에서 target_name이 선언된 타겟이 아닐 때의 분기)에 Go용 체크를 추가하는 구조로 감. 다만 C/C++와 달리:
- 파일명 매칭(stem)이 아니라 **실제 존재하는 파일 경로**로 판별 (`cmd/colorpicker-preview/main.go`처럼 슬래시 포함).
- 같은 언어의 기존 타겟에서 설정을 빌려올 필요가 없음(Go는 `go.mod`가 버전/설정을 다 가지고 있어서) -- **stoke.toml에 Go 타겟이 하나도 없어도 동작함**.
- `stoke build`를 거치지 않고 `go run`으로 컴파일+실행을 한 번에 위임 -- "이 파일 한 번 돌려봐"라는 의도와 정확히 일치, 영속 바이너리를 stoke가 따로 관리할 필요 없음.

## 변경

`src/stoke/cli/build.py`:
- `_find_adhoc_go_entry(project_root, path_str)` -- `project_root / path_str`가 실제 존재하는 `.go` 파일이면 반환, 그 외엔 `None`. 파일을 열어보지 않음.
- `_run_adhoc_go_entry(project_root, entry_file)` -- `entry_file`의 부모 디렉토리를 패키지 경로로 계산(`cmd/colorpicker-preview/main.go` → `./cmd/colorpicker-preview`, 프로젝트 루트 직속 파일이면 `.`), `tool_install.toolchain_env("go", ...)`로 프로젝트 로컬/PATH의 `go` 실행 파일을 찾아서 `go run <패키지 경로>` 그대로 실행.
- `cmd_run()`의 기존 C/C++ ad-hoc 체크 바로 다음에 Go 체크 추가 -- 둘 다 매칭 안 되면 기존 흐름(선언된 타겟 이름 해석)으로 그대로 폴백.

## 검증

실제 사용자가 겪었던 상황을 그대로 재현해서 확인:
- `carty`라는 타겟 하나만 있는 프로젝트에서 `cmd/colorpicker-preview/main.go` 생성 → `stoke run cmd/colorpicker-preview/main.go` 실행 → **정상적으로 `go run ./cmd/colorpicker-preview`가 실행되고 프로그램 출력까지 나오는 것 확인** (전에는 "target not found" 에러였음).
- 출력 순서 버그 발견: "Ad hoc: go run ..." 안내 메시지가 자식 프로세스 출력보다 늦게 찍히는 버퍼링 문제 → `print(..., flush=True)`로 수정, 순서 정상화 확인.
- **프로젝트 루트 직속 파일** (`roottool.go`, 부모 디렉토리 = 프로젝트 루트라 패키지 경로 `.`) → 프로젝트 루트에 이미 있던 `stoke init`의 예시 `main.go`와 같은 패키지에서 `main()`이 중복돼서 Go 컴파일러가 정확히 "main redeclared" 에러를 내는 것 확인 -- **stoke가 아니라 Go 컴파일러가 검사한다는 설계 의도가 실제로 그대로 동작**.
- 선언되지 않은 진짜 엉뚱한 이름(`totally-bogus-target`, 파일도 아님)을 줬을 때는 기존 그대로 "target not found" 에러로 폴백하는 것도 재확인 (회귀 없음).

## 적용 안 한 것

- Rust/Kotlin/C#/Ruby/PHP 등 다른 언어의 ad-hoc 파일 경로 실행 -- 이번엔 사용자가 실제로 겪은 Go 케이스만. Rust는 `cargo run --bin`이 있어서 비슷하게 확장 가능해 보이지만 범위 밖.
