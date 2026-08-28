# 기능 현황

무엇이 검증됐고, 무엇이 남은 gap이고, 대규모 조직에 맞는지 정리. 각 기능이 어떻게 동작하는지는 [메인 README](../README.md) / [전체 문서](./README_ko.md) 참고.

## 검증됨

- **Python, Java, C, C++** — 가장 먼저 나온 4개 언어. 빌드/실행/watch/hot-reload, IDE 통합(VSCode/IntelliJ/Eclipse), 빌드 캐시(content-hash + 원격/공유 캐시), lock 파일 모두 end-to-end로 검증됨. Windows에서는 gcc/clang뿐 아니라 MSVC(`compiler = "msvc"`)도 포함.
- **Go, JavaScript, TypeScript** — 빌드/실행/watch/hot-reload와 버전 pin(`go.mod`, `.nvmrc`/`engines.node`)이 프레임워크 스캐폴딩(Gin, Echo, Fiber, Chi, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono) 전반에서 검증됨.
- **버전 pinning** — 각 언어의 pin 방식(문서의 [버전 pin](./README_ko.md#팀-일관성을-위한-버전-pin) 섹션 참고)이 언어당 최소 한 프로젝트에서 검증됨.
- **사설 레지스트리/미러 지원** — Sonatype Nexus(버전 JSON용 `raw` hosted repo, Java 의존성용 `maven-central` 프록시) 기준으로 Basic Auth 포함 검증됨.
- **빌드 캐시** — content-hash 무효화가 새 체크아웃(새 mtime, 같은 내용)에서도 캐시를 정확히 재사용함을 검증; 원격 캐시는 디렉토리를 공유하는 두 대의 머신 간에 검증됨.
- **Pre/post-build 훅** — `stoke build`, `stoke build --all`, `stoke watch`, `stoke hot-reload` 전부에서 모든 언어 기준으로 검증됨.
- **플러그인 시스템** (`stoke.languages` / `stoke.frameworks` entry point) — 두 entry point 그룹을 모두 등록하는 독립 예제 플러그인 패키지로 검증됨.
- **멀티 타겟 프로젝트** — 기존 `stoke.toml`에 타겟을 추가/제거하는 것이 언어별 프로젝트 루트 등록(Cargo 워크스페이스 멤버, Gradle `settings.gradle.kts`의 include, C# 루트 `.csproj`의 exclude 등) 전부에 대해 검증됨.

## 남은 gap

- macOS/Linux 네이티브 설치파일 아직 없음 (pip는 되지만 end-to-end 검증은 안 됨) — Windows에만 번들 설치파일 제공.
- C/C++용 CMake/Meson 통합 없음 — stoke는 자체 단순 빌드 모델이라 대형/생성형 C/C++ 빌드 그래프는 안 맞음.
- 플러그인 기반 언어는 대화형 `stoke init` 마법사에 자동으로 항목이 생기지 않음 — `stoke init`을 직접 지원하려면 플러그인 쪽에서 `stoke.frameworks` entry point를 따로 등록해야 함.
- Rust, Kotlin, C#, Ruby, PHP는 가장 최근에 추가된 언어라 커맨드 생성/템플릿은 검증됐지만 각 생태계의 대형 실전 프로젝트로는 아직 충분히 검증 안 됨.
- 타겟 간 의존성 그래프 없음 — `stoke build --all`은 모든 타겟을 독립적이라고 가정.
- Rails, Laravel 스캐폴딩은 의도적으로 제외 — 둘 다 entry 스크립트를 직접 실행하는 대신 CLI 서브커맨드(`bin/rails server`, `php artisan serve`)로 시작하는 구조라 stoke의 실행 모델과 안 맞음.

## 대규모 조직에 맞는가

stoke는 큰 팀이 보통 필요로 하는 요소들을 갖추고 있음: 재현 가능한 빌드(lock 파일), 12개 언어 전체에 걸친 팀 단위 툴체인 버전 일관성(pinning), CI 체크아웃을 넘나들고 여러 머신 간 공유도 되는 빌드 캐시, 폐쇄망을 위한 사설 레지스트리/미러 지원. Pre/post-build 훅과 플러그인 시스템 덕분에 플랫폼 팀이 stoke를 포크하지 않고도 확장할 수 있음.

폭넓게 도입하기 전에 따져볼 부분: macOS/Linux 설치파일이 아직 없고(pip는 되지만 다듬어진 경로는 아님), 모노레포 스타일 멀티 타겟 프로젝트에서 타겟 간 의존성 그래프가 없으며, 가장 최근에 추가된 5개 언어(Rust, Kotlin, C#, Ruby, PHP)는 코드 경로 자체는 검증됐지만 아직 대형 실전 프로젝트를 거치지 않음. 이 중 구조적으로 막는 문제는 없지만, 현재 시점에 우회가 가장 필요할 가능성이 높은 지점들임.
