# 프로젝트 로컬 전용 Go 툴체인은 gopls/Mason 같은 에디터 툴링과 충돌함 — 결국 시스템 설치가 필요

- 날짜: 2026-09-18
- 심각도: design (미해결, 코드 수정 없음 — 결정 필요)
- 상태: 미해결 — 방향 논의만 하고 결론은 안 냄

## 배경

`stoke exec`([2026-09-18 [design] project-local toolchains unreachable from user shell.md](<2026-09-18 [design] project-local toolchains unreachable from user shell.md>))로 "사용자가 셸에서 직접 치는 명령"까지는 해결했는데, 그다음 실제로 부딪힌 사례: Neovim의 Mason이 `gopls`(Go 언어 서버)를 설치하려고 내부적으로 `go install`을 실행함. `go`는 Go로 작성된 프로그램(`gopls`)을 빌드하는 컴파일러라서 이 과정 자체에 `go` 실행파일이 필요한데, Mason은 완전히 별개의 프로세스(에디터 플러그인)라 `stoke exec`가 절대 개입할 수 없음 — 시스템 PATH에 `go`가 없으면 무조건 실패.

## 문제의 핵심

stoke는 Go를 `.stoke/toolchains/go-<version>/`에 프로젝트 로컬로만 설치하고 시스템 PATH는 절대 안 건드리는 게 설계 원칙(다른 언어도 전부 동일). 이 원칙 덕분에 stoke가 직접 실행하는 경로(`build`/`run`/`test`/`exec`)는 시스템에 go가 전혀 없어도 다 동작함. 그런데:

- 에디터 LSP 서버 설치(Mason, VSCode Go 확장의 `go install` 계열 도구들 — `gopls`, `dlv`, `golangci-lint` 등)
- 그 외 stoke를 안 거치는 모든 도구/스크립트

는 전부 시스템 PATH만 보기 때문에, "이 프로젝트는 stoke로만 빌드한다"는 전제가 실제로는 잘 안 맞음 — 실무에서는 결국 에디터 툴링 때문에라도 시스템에 진짜 `go`가 있어야 함.

## 논의된 내용

- `.stoke/toolchains/go-*/go/bin`을 셸 설정 파일에 영구 등록하는 방법도 있지만, stoke가 나중에 다른 버전으로 재설치하면 경로(버전 문자열)가 바뀌어서 셸 설정을 매번 고쳐야 함 — 유지보수 부담
- 결국 `sudo apt install golang-go`(또는 OS별 동일한 전역 설치)가 정석이라는 결론. stoke의 project-local 툴체인과 시스템 설치는 공존 가능 — `_find_go()`가 항상 `.stoke/toolchains/`를 시스템 PATH보다 먼저 보므로 버전 pin은 여전히 유효
- 그렇다면 "프로젝트별 Go 격리 설치"가 실제로 주는 가치는 **버전 재현성**(팀/CI에서 다들 같은 버전으로 빌드)뿐이고, "시스템에 go 없이도 개발 가능"이라는 원래 취지는 에디터 툴링 앞에서 절반만 성립한다는 게 드러남
- 1인 개발/로컬 전용 프로젝트에서는 이 격리 기능의 이득이 거의 없고(시스템 go 하나로 빌드도 에디터도 다 해결됨), 여러 프로젝트가 서로 다른 Go 버전을 요구하거나 팀/CI에서 버전 통일이 필요한 경우에만 실익이 있음

## 아직 안 정한 것 (다음에 결정 필요)

1. `stoke install go` 실행 시 안내 문구에 "에디터 LSP/도구를 쓰려면 시스템에도 go를 따로 설치하는 걸 권장" 같은 경고를 추가할지
2. 아니면 이건 stoke가 신경 쓸 범위가 아니라고 보고 문서(`HOW_TO_USE.md` 등)에만 한 줄 남길지
3. `stoke exec`가 나온 김에, 아예 `.stoke/toolchains/<lang>-*`를 툴체인 존재 시 "필요하면 심볼릭 링크나 shim으로 노출" 같은 추가 기능을 만들지 (범위가 커질 수 있어 신중히 검토 필요)

이번 세션에서는 코드 변경 없이 이 트레이드오프만 정리해둠 — 어떤 방향으로 갈지는 다음에 결정.
