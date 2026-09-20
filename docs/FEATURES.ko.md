# 기능 현황

무엇이 검증됐고, 무엇이 남은 gap이고, 대규모 조직에 맞는지 정리. 각 기능이 어떻게 동작하는지는 [메인 README](../README.md) / [전체 문서](./README_ko.md) 참고.

## 검증됨

- **Python, Java, C, C++** — 가장 먼저 나온 4개 언어. 빌드/실행/watch/hot-reload, IDE 통합(VSCode/IntelliJ/Eclipse), 빌드 캐시(content-hash + 원격/공유 캐시), lock 파일 모두 end-to-end로 검증됨. Windows에서는 gcc/clang뿐 아니라 MSVC(`compiler = "msvc"`)도 포함.
- **Go, JavaScript, TypeScript** — 빌드/실행/watch/hot-reload와 버전 pin(`go.mod`, `.nvmrc`/`engines.node`)이 프레임워크 스캐폴딩(Gin, Echo, Fiber, Chi, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono) 전반에서 검증됨.
- **버전 pinning** — 각 언어의 pin 방식(문서의 [버전 pin](./README_ko.md#팀-일관성을-위한-버전-pin) 섹션 참고)이 언어당 최소 한 프로젝트에서 검증됨.
- **사설 레지스트리/미러 지원** — Sonatype Nexus(버전 JSON용 `raw` hosted repo, Java 의존성용 `maven-central` 프록시) 기준으로 Basic Auth 포함 검증됨.
- **빌드 캐시** — content-hash 무효화가 새 체크아웃(새 mtime, 같은 내용)에서도 캐시를 정확히 재사용함을 검증; 원격 캐시는 디렉토리를 공유하는 두 대의 머신 간에 검증됨.
- **Pre/post-build 훅** — `stoke build`, `stoke watch`, `stoke hot-reload` 전부에서 모든 언어 기준으로 검증됨.
- **플러그인 시스템** (`stoke.languages` / `stoke.frameworks` entry point) — 두 entry point 그룹을 모두 등록하는 독립 예제 플러그인 패키지로 검증됨.
- **CMake 위임** (`build_system = "cmake"`) — Windows(MSVC/Visual Studio generator)에서 end-to-end 검증: `stoke build`/`run`/`clean`이 `cmake`로 configure+build하고 결과 실행 파일을 찾아내며, `stoke watch`/`hot-reload`의 기존 재빌드-재시작 루프를 코드 수정 없이 그대로 재사용.
- **Meson 위임** (`build_system = "meson"`) — meson+ninja로 end-to-end 검증: `stoke build`/`run`/`clean`이 `meson setup`/`meson compile`로 configure+compile하고 결과 실행 파일을 찾아내며, CMake 경로와 같은 `stoke watch`/`hot-reload` 루프를 재사용.

## 남은 gap


- 플러그인 기반 언어는 대화형 `stoke init` 마법사에 자동으로 항목이 생기지 않음 — `stoke init`을 직접 지원하려면 플러그인 쪽에서 `stoke.frameworks` entry point를 따로 등록해야 함.
- Rust, Kotlin, C#, Ruby, PHP는 가장 최근에 추가된 언어라 커맨드 생성/템플릿은 검증됐지만 각 생태계의 대형 실전 프로젝트로는 아직 충분히 검증 안 됨.
- Rails, Laravel 스캐폴딩은 의도적으로 제외 — 둘 다 entry 스크립트를 직접 실행하는 대신 CLI 서브커맨드(`bin/rails server`, `php artisan serve`)로 시작하는 구조라 stoke의 실행 모델과 안 맞음.
- 모노레포는 서비스마다 `stoke.toml` 하나씩 — 한 파일에 `[targets.*]`를 여러 개 넣는 방식이 아님. lock 파일이 언어당 버전 슬롯 하나뿐이라, 같은 언어 타겟 2개를 한 `stoke.toml`에 넣으면 서로 lock 정보를 덮어씀. `stoke init --workspace` + `stoke new <name> -l <language>`로 세팅: 타겟 없는 루트 `stoke.toml` 하나 + 서비스 서브디렉토리마다 독립된 `stoke.toml`/`stoke.lock`. `stoke build --all`/`stoke test --all`이 루트에서 멤버 전체를 순차 실행함.
- `stoke audit`(CVE 스캔)과 `stoke outdated`(버전 뒤처짐 확인)는 언어 지원 범위가 동일함: Kotlin, C, C++는 아직 미지원이고, Go/Rust/Ruby는 해당 도구(`govulncheck`/`cargo-audit`/`bundler-audit`, `stoke outdated`는 `cargo-outdated`)가 이미 설치돼 있어야만 동작함 — stoke가 대신 설치해주진 않음.
- `stoke sbom`은 audit/outdated보다 지원 언어가 적음: Python, Java, Go, Rust, JavaScript/TypeScript만 지원. C#, Ruby, PHP, Kotlin, C, C++는 아직 미지원.

## 대규모 조직에 맞는가

stoke는 큰 팀이 보통 필요로 하는 요소들을 갖추고 있음: 재현 가능한 빌드(lock 파일), 12개 언어 전체에 걸친 팀 단위 툴체인 버전 일관성(pinning), CI 체크아웃을 넘나들고 여러 머신 간 공유도 되는 빌드 캐시, 폐쇄망을 위한 사설 레지스트리/미러 지원, 의존성 취약점 스캔(`stoke audit`)까지. Pre/post-build 훅과 플러그인 시스템 덕분에 플랫폼 팀이 stoke를 포크하지 않고도 확장할 수 있음. 단일 실행 파일로 배포되므로 CI 러너나 Docker 빌드 스테이지에 언어 런타임을 미리 깔 필요도 없음 — GitHub Actions/Dockerfile 예제는 [docs/ci/](./ci/) 참고.

폭넓게 도입하기 전에 따져볼 부분 하나: 가장 최근에 추가된 5개 언어(Rust, Kotlin, C#, Ruby, PHP)는 코드 경로 자체는 검증됐지만 아직 대형 실전 프로젝트를 거치지 않음. 구조적으로 막는 문제는 아니지만, 현재 시점에 우회가 가장 필요할 가능성이 높은 지점.
