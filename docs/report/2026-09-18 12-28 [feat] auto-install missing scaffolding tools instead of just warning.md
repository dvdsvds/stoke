# 스캐폴딩 중 툴 없으면 자동 설치 제안

- 날짜: 2026-09-18
- 종류: feat

## 배경

`stoke init gin`을 `go` 없는 환경에서 실행하면:

```
Warning: 'go' not found. Run these manually:
  go mod init github.com/dvdsvds/carty
  go get github.com/gin-gonic/gin
```

이렇게 경고만 찍고 사용자가 수동으로 명령어를 쳐야 했음. stoke는 언어 툴체인을 프로젝트 로컬(`.stoke/toolchains/`, 전역 상태 안 건드림)로 설치해주는 `stoke install <language>` 기능이 이미 있는데, 스캐폴딩 단계에서는 이걸 안 쓰고 있었음 — stoke의 취지(프로젝트별 툴체인 관리)와 안 맞는 부분.

## 변경

`src/stoke/tool_install.py` 추가:

- `ensure_tool(language, exe_names, project_path, display_name)`: PATH나 `.stoke/toolchains/<language>-*/`에 실행파일이 있으면 그 경로 반환. 없으면 "지금 설치할까요? (Y/n)" 물어보고, 승낙하면 `stoke install <language>`를 프로젝트 디렉토리 기준으로 실행한 뒤 새로 생긴 실행파일을 찾아 반환. 거절/실패하면 `None` — 호출부는 기존 수동 안내로 폴백.
- `ensure_cargo(project_path)`: cargo 전용. rustup으로 설치된 cargo는 `RUSTUP_HOME`/`CARGO_HOME` 환경변수가 있어야 동작하는 얇은 프록시라서(`rust/adapter.py`의 기존 로직과 동일), 실행파일 경로만 주는 `ensure_tool`로는 부족해 `(exe_path, env)` 튜플을 반환하도록 별도로 둠.
- `ensure_bundle(project_path)`: `stoke install ruby`는 Ruby 자체만 보장하고 Bundler는 별도 gem이라, ruby부터 확보한 뒤 그 ruby의 `gem`으로 `gem install bundler`까지 자동으로 해줌.

## 적용 범위

| 언어 | 적용 파일 | 방식 |
|---|---|---|
| Go | `go/init.py`, `frameworks/{gin,echo,fiber,chi}.py` | `ensure_tool("go", ...)` |
| Rust | `rust/init.py`, `frameworks/{actix_web,axum,rocket}.py` | `ensure_cargo()` |
| C# | `csharp/init.py`, `frameworks/aspnet_core.py` | `ensure_tool("csharp", ("dotnet","dotnet.exe"), ...)` |
| Ruby | `frameworks/sinatra.py` | `ensure_bundle()` |
| JS | `frameworks/{express,fastify}.py` | `ensure_tool("nodejs", ("npm","npm.cmd"), ...)` |

## 적용 안 한 것 (이유 있음)

- **Kotlin (gradle)**: `stoke install kotlin`은 JDK만 설치함(`_NO_DIRECT_INSTALL`에 등록되어 있어서 stoke 자체가 "Kotlin 컴파일러는 Gradle이 관리한다"고 명시). "gradle이 없다"는 문제 자체를 이 메커니즘으로 못 고침. Gradle wrapper 스크립트를 정적 파일로 직접 심는 방법은 있지만 이번 작업 범위 밖.
- **PHP (composer)**: `stoke install php`는 PHP 인터프리터만 주고 Composer는 완전히 별도 설치 스크립트(`composer-setup.php`)라 stoke가 관리하는 대상이 아님.
- **TypeScript npx 기반 스캐폴더 (nextjs/nuxt/sveltekit/hono/vite/nestjs)**: 작업 중 발견한 별개 이슈 — 이 6개 프레임워크는 **stoke.toml을 아예 안 씀** (아래 별도 문서 참고). `stoke install`이 동작하려면 프로젝트 루트에 stoke.toml이 있어야 하는데 그게 없어서 이 메커니즘을 못 씀.

## 검증

- `_find_toolchain_exe`/`_find_toolchain_dir`를 가짜 `.stoke/toolchains/go-*`, `rust-*` 디렉토리 구조로 직접 테스트해서 탐색 로직 확인
- `ensure_tool`/`ensure_cargo`가 PATH에 이미 있는 도구는 프롬프트 없이 바로 반환하는 것 확인, 설치 거절 시 예외 없이 `None` 반환하는 것 확인
- 모든 변경 파일 `py_compile` + import 확인

## 변경 파일

- `src/stoke/tool_install.py` (신규)
- Go/Rust/C#/Ruby/JS 프레임워크·init 파일 15개
