# 다른 언어 스캐폴딩에서도 install 실패가 조용히 묻힘

- 날짜: 2026-09-17
- 심각도: bug (JS/TS의 `shell=True` 버그와 다른 종류지만 같은 계열의 문제)
- 상태: 수정됨
- 관련: [2026-09-17 [critical][fixed] npm install silently skipped during JS-TS scaffolding.md](<2026-09-17 [critical][fixed] npm install silently skipped during JS-TS scaffolding.md>)

## 배경

JS/TS 프레임워크 핸들러에서 발견한 `shell=True` + 리스트 인자 버그를 고친 뒤, 같은 종류의 문제가 다른 언어에도 있는지 전수 감사함. `shell=True` + 리스트 조합 자체는 JS/TS 외에 없었음(`src/stoke/languages/_node_tools.py:75`도 `shell=(sys.platform == "win32")`로 Windows에서만 켜지고, Windows에서는 이 조합이 `list2cmdline()`으로 정상 처리되므로 문제 없음).

다만 **다른 패턴의 버그**가 6개 언어, 16개 파일에 퍼져 있었음: 스캐폴딩용 subprocess 호출이 `capture_output=True`로 출력을 삼키고 **리턴코드를 체크하지 않음** — install/setup이 실패해도 CLI는 성공했다고 보여주고, 프로젝트는 반쯤 깨진 채로 남음. express의 `shell=True` 버그와 증상(조용한 실패)은 같고 원인만 다름.

## 발견된 위치

| 언어 | 파일 | 실패해도 조용히 넘어가는 명령어 |
|---|---|---|
| Kotlin | `src/stoke/languages/kotlin/init.py:65-69` | `gradle wrapper --gradle-version ...` |
| Kotlin | `src/stoke/languages/kotlin/frameworks/spring_boot.py:27-31` | `gradle wrapper` |
| Kotlin | `src/stoke/languages/kotlin/frameworks/ktor.py:26-30` | `gradle wrapper` |
| Go | `src/stoke/languages/go/init.py:55-59` | `go mod init <name>` |
| Go | `src/stoke/languages/go/frameworks/fiber.py:26-36` | `go mod init` + `go get .../fiber/v2` |
| Go | `src/stoke/languages/go/frameworks/echo.py:26-36` | `go mod init` + `go get .../echo/v4` |
| Go | `src/stoke/languages/go/frameworks/chi.py:26-36` | `go mod init` + `go get .../chi/v5` |
| Go | `src/stoke/languages/go/frameworks/gin.py:26-36` | `go mod init` + `go get .../gin` (go 자체가 없을 때 안내는 있지만, `go get` 실패는 그대로 무시) |
| Rust | `src/stoke/languages/rust/init.py:50-54` | `cargo init --name <name> --vcs none` |
| Rust | `src/stoke/languages/rust/frameworks/rocket.py:23-27` | `cargo check` |
| Rust | `src/stoke/languages/rust/frameworks/actix_web.py:23-27` | `cargo check` |
| Rust | `src/stoke/languages/rust/frameworks/axum.py:23-27` | `cargo check` |
| C# | `src/stoke/languages/csharp/init.py:51-55` | `dotnet new console --name ... --force` |
| C# | `src/stoke/languages/csharp/frameworks/aspnet_core.py:20-23` | `dotnet new web --name ... --force` |
| Ruby | `src/stoke/languages/ruby/frameworks/sinatra.py:23-27` | `bundle install` |
| PHP | `src/stoke/languages/php/frameworks/slim.py:24-28` | `composer install` |

경미(영향 작음): `src/stoke/languages/python/adapter.py:510-513`의 `conda env remove --prefix ... --yes`도 리턴코드 체크가 없지만, 바로 뒤에 `shutil.rmtree`로 같은 디렉토리를 한 번 더 지우는 안전망이 있어서 실질적 영향은 작음.

## 영향 안 받는 곳 (확인 완료)

핵심 build/run/test 경로 — `cmake_adapter.py`, `meson_adapter.py`, `vcpkg.py`, `npm_check.py`, 각 언어의 `adapter.py`(python/java/kotlin/go/rust/csharp/ruby/php/c/cpp) — 는 전부 리턴코드 체크와 stderr 출력을 제대로 하고 있음. 문제는 딱 "stoke init <framework>" 스캐폴딩 단계에만 몰려 있음.

## 수정

express/fastify에 적용한 패턴과 동일하게, 위 16개 호출부 전부에 리턴코드 체크 + 실패 시 stderr 출력을 추가함. 각 파일에서 `result = subprocess.run(..., capture_output=True, text=True)` 후 `if result.returncode != 0: print(...stderr...)` 형태로 통일. 전부 `py_compile`로 문법 확인 완료.
