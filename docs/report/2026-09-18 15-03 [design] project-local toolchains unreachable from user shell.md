# 프로젝트 로컬 전용 툴체인이 사용자 셸/네이티브 도구 명령에서 접근 불가능함

- 날짜: 2026-09-18
- 심각도: design (기능 누락, 버그는 아님)
- 상태: 해결됨 — `stoke exec` 신설 (아래 "구현" 참고)

## 문제

`stoke install`(그리고 `stoke init`이 내부에서 호출하는 자동 설치)은 언어 툴체인을 `.stoke/toolchains/<lang>-*/`에 프로젝트 전용으로 설치하고, **의도적으로 시스템 PATH를 건드리지 않음** (`install_lang.py`에 명시: "PATH는 전혀 안 건드림... stoke build/run이 알아서 찾음"). 이건 "언어/툴체인을 프로젝트별로 격리하고 전역 상태를 안 건드린다"는 stoke의 설계 원칙상 의도된 동작.

문제는 이 설계가 stoke가 직접 실행하는 명령(`stoke build`/`run`/`test`)에만 적용되고, **사용자가 직접 셸에서 치는 네이티브 도구 명령**은 전혀 커버하지 못한다는 것. 예:

- `go mod tidy`, `go vet`
- `cargo add <crate>`, `cargo update`
- `bundle add <gem>`
- `composer require <package>`
- `dotnet add package <name>`
- 손으로 치는 `npm install <pkg>` (참고: `stoke add`/`stoke remove`로 처리 가능한 경우도 있으나 별도 버그 있음 — [2026-09-18 [bug][high] stoke add-remove for JS-TS ignores project-local Node toolchain.md](<2026-09-18 [bug][high] stoke add-remove for JS-TS ignores project-local Node toolchain.md>))

이 명령들은 전부 시스템 PATH만 보기 때문에, 해당 언어가 시스템에 전혀 설치돼 있지 않고 stoke가 프로젝트 로컬로만 설치한 환경에서는 전부 실패함. `stoke.toml`이 실제 매니페스트가 아닌 모든 언어(Go/Rust/C#/Ruby/PHP — Kotlin은 Gradle에 위임)에서 동일하게 해당하고, Node.js도 `stoke add`/`remove`가 다루지 못하는 명령(예: `npm audit`, `npx <tool>`)에는 동일하게 해당함.

## 실사례

`stoke init bubbletea`로 만든 Go 프로젝트에서, `go get`이 잘못 표시한 `// indirect`를 고치려고 사용자가 직접 `go mod tidy`를 실행했더니 "go: command not found" — 시스템에 Go가 아예 없고, stoke가 `.stoke/toolchains/go-1.26.5/`에 프로젝트 전용으로 받아둔 것뿐이었기 때문. (`stoke build`는 내부적으로 그 경로를 직접 호출하니 정상 동작.)

## 현재 가능한 임시 우회

프로젝트 루트에서 해당 세션에만 PATH를 잡아서 실행:

```bash
PATH="$PWD/.stoke/toolchains/go-1.26.5/bin:$PATH" go mod tidy
```

(언어마다 `.stoke/toolchains/` 밑 실제 실행파일 위치가 다름 — 압축 레이아웃이 언어별로 제각각이라 매번 직접 찾아야 함.)

## 검토한 옵션

1. **사용자가 매번 수동으로 PATH를 잡아서 실행** — 지금 유일하게 되는 방법. 매번 실제 툴체인 디렉토리 이름(버전 포함)을 확인해야 해서 번거롭고, 언어마다 내부 레이아웃이 달라 명령이 다 다름.
2. **`stoke exec`(가칭) 같은 passthrough 명령 추가** — 예: `stoke exec -- go mod tidy`, `stoke exec -- cargo add serde` 처럼 현재 타겟의 언어를 보고 해당 프로젝트 로컬 툴체인의 `bin/`을 PATH 맨 앞에 얹은 서브프로세스로 임의 명령을 실행. `stoke.toml`의 `[targets.X]`에서 language를 읽고, 각 어댑터가 이미 갖고 있는 `_find_toolchain_dir`류 로직을 재사용하면 구현 자체는 크지 않음 (Go/Rust/C#/Ruby/PHP/Node.js 어댑터에 이미 존재하는 "프로젝트 로컬 우선, 없으면 PATH" 탐색 로직을 공용 헬퍼로 추출해서 `stoke exec`와 각 어댑터가 같이 쓰는 형태 추천).

## 참고

`stoke mod tidy`처럼 언어별 서브커맨드를 개별로 추가하는 방식은 언어마다 대응하는 네이티브 명령 개수가 다르고(`cargo`만 해도 `add`/`update`/`tidy`에 해당하는 하위 명령이 여러 개) 계속 따라가야 해서 확장성이 떨어짐 — 범용 passthrough(옵션 2) 쪽으로 결정.

## 구현

`src/stoke/cli/exec_cmd.py` 신규: `stoke exec [--target=X] -- <command...>`.

- 타겟의 `language`를 보고, 각 어댑터가 이미 쓰는 것과 동일한 탐색 로직으로 프로젝트 로컬 툴체인을 찾음:
  - Go/C#/Ruby/PHP: `tool_install.py`의 `_find_toolchain_exe(project_root, language, exe_name)`로 실행파일을 찾아 그 `bin/`을 PATH 맨 앞에 얹음
  - Rust: `_find_toolchain_dir`로 `.stoke/toolchains/rust-*/`를 찾아서 `RUSTUP_HOME`/`CARGO_HOME`을 설정하고 `cargo/bin`을 PATH에 얹음 (`ensure_cargo`/`RustAdapter._find_cargo()`와 동일한 방식 — cargo는 rustup 프록시라 PATH만으론 부족함)
  - JavaScript/TypeScript: `_node_tools.find_local_node_dir()`로 Node 설치를 찾아서 그 `bin/`을 PATH에 얹음
  - 못 찾으면 `os.environ`을 그대로 써서 기존 동작(시스템 PATH만 봄)과 동일하게 폴백
- 프로젝트 로컬 실행파일 자체를 직접 실행하는 게 아니라 **PATH/환경변수만 준비하고 사용자가 지정한 명령을 그대로 실행** — 아무것도 설치하지 않고 전역 상태도 안 건드림(자식 프로세스 하나에만 적용되는 `env=` 딕셔너리).
- `--` 뒤에 오는 임의 명령을 그대로 넘겨야 해서 `command_args`는 `argparse.REMAINDER`로 받음. 최상위 서브파서 dispatch가 `dest="command"`를 이미 쓰고 있어서 이름 충돌을 피하려고 `command_args`로 명명(표시상 메타변수는 `command`).
- CLI 등록: `src/stoke/cli/__init__.py`에 `exec` 서브파서 + dispatch 분기 추가, `src/stoke/cli/messages.py`에 en/ko `exec.*` 메시지 추가.
- 문서: `README.md`, `docs/README_ko.md`, `docs/HOW_TO_USE.md`, `docs/HOW_TO_USE_KO.md`에 `stoke exec` 사용법 추가.
- 검증: 가짜 `.stoke/toolchains/go-1.26.5/go/bin/go` 스크립트를 만들어 `stoke exec -- go mod tidy`가 시스템 PATH에 go가 전혀 없어도 그 프로젝트 로컬 실행파일을 정확히 찾아 쓰는 것 확인. `--target` 처리, 명령 누락 시 에러 처리도 확인. 이후 시스템에 실제 Go 1.26.0을 설치한 뒤 `stoke exec -- go mod tidy`를 실제 gin 프로젝트에서 실행해서 exit 0으로 정상 동작하는 것도 재확인.
