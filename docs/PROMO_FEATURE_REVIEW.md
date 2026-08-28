# stoke 기능 정리 (홍보용 검토)

코드(src/stoke)와 CLI 진입점(cli/__init__.py), stoke.toml 스키마(config.py)를 직접 읽고 정리함. README/FEATURES.md의 주장과 실제 코드가 일치하는지 대조함.

## 1. 핵심: 12개 언어 빌드/실행

`stoke.toml` 하나로 Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript를 빌드/실행.

- `stoke build [target] [--force] [--all] [--debug|--release]` — 빌드. `--all`은 여러 타겟을 병렬 빌드하되, `depends_on`으로 선언한 의존성은 먼저 끝내고 순서를 지킴 (2026-08-29 추가)
- `stoke run [target]` — 실행
- `stoke watch [target]` — 파일 변경 감지 후 자동 재빌드 (watchdog 기반)
- `stoke hot-reload [target]` — 재시작 없이 변경 반영 (언어별 구현 다름)
- `stoke clean [target] [--all]` — 빌드 산출물 정리 (`--all`은 lock 파일도 삭제)

검증 상태(FEATURES.md 기준): Python/Java/C/C++는 end-to-end 검증됨. Go/JS/TS도 검증됨. Rust/Kotlin/C#/Ruby/PHP는 "명령어 구성과 템플릿은 검증했지만 대규모 실전 프로젝트 검증은 아직" — 가장 최근에 추가된 5개 언어라 홍보 문구에서 신뢰도를 과장하지 않는 게 좋음.

## 2. 프로젝트 스캐폴딩 (`stoke init`)

`stoke init <type>`로 24개 프레임워크 템플릿 생성 (cli/__init__.py의 `_INIT_FRAMEWORK_HANDLERS` 확인):

| 언어 | 프레임워크 |
|---|---|
| Python | FastAPI, Flask, Django |
| Java | Spring Boot |
| Kotlin | Ktor, Spring Boot |
| Go | Gin, Echo, Fiber, Chi |
| Rust | Actix Web, Axum, Rocket |
| C# | ASP.NET Core |
| Ruby | Sinatra |
| PHP | Slim |
| JavaScript | Express, Fastify |
| TypeScript | Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono |

- 대화형 마법사(`stoke init`, 인자 없이) 또는 비대화형(`--language --name --version --env-type --lock-mode --vcpkg --yes`)으로 실행 가능 → CI/스크립트에서 쓰기 좋은 부분, 홍보 포인트로 괜찮음.
- `--remove-target <name> --yes`로 기존 프로젝트에서 타겟 제거도 지원 (언어별 등록 해제까지 처리: Cargo workspace, Gradle settings, .csproj 등).
- **의도적으로 뺀 것**: Rails, Laravel. 이유가 코드에 명시돼 있음 — `bin/rails server`, `php artisan serve`처럼 CLI 서브커맨드로 뜨는 프레임워크라 stoke의 "엔트리 스크립트 직접 실행" 모델과 안 맞음. 이건 버그가 아니라 설계상 제외이므로 홍보에서 "24개 프레임워크"라고만 하고 Rails/Laravel을 기대하게 만들지 않는 게 좋음.

## 3. 언어/툴체인 설치

- `stoke install --language <python|java|c|cpp|go|node> [--version] [--list] [--base-url]` — 버전 매니저 없이 stoke가 직접 설치. Rust/Kotlin/C#/Ruby/PHP는 자체 설치 도구(rustup 등)로 위임 (직접 설치 지원 안 함).
- `stoke uninstall --language ...`
- `--base-url` / `STOKE_VERSION_API_BASE`로 사내 미러 서버 지정 가능 (폐쇄망 대응)

## 4. C/C++ 전용 기능

- `stoke vcpkg install/remove/list/version`, `stoke install vcpkg` — vcpkg 라이브러리 매니저 연동
- 빌드 프로파일(`[profiles.*]`) — debug/release 기본 제공 + 커스텀 프로파일, `compiler = "msvc"`로 Windows에서 MSVC 지정 가능 (gcc/clang과 나란히)
- `build_system = "cmake"` (2026-08-29 추가) — 이미 `CMakeLists.txt`가 있는 C/C++ 타겟은 stoke 자체 컴파일 모델 대신 cmake configure/build로 위임. `build`/`run`/`watch`/`hot-reload`/`clean` 전부 그대로 씀. Meson은 여전히 미지원. c_standard/profile 필드는 이 경로에서 무시됨(CMakeLists.txt가 관리) — 홍보에서 "기존 CMake 프로젝트도 그대로 붙는다"는 정확하지만, "표준/컴파일 플래그도 stoke.toml로 관리된다"는 이 경로에서는 틀림.

## 5. 버전 고정 (Version Pinning)

언어별로 실제 표준 파일에 씀 (stoke 자체 락파일이 아니라 각 생태계가 이미 읽는 파일):
- Go → `go.mod`의 `go`/`toolchain`
- Node(JS/TS) → `.nvmrc` + `package.json`의 `engines.node`
- Rust → `rust-toolchain.toml`
- 나머지 언어도 각자 방식으로 지원

팀원/CI가 같은 버전으로 빌드하게 강제하는 기능 — 실질적 가치가 명확한 기능.

## 6. 빌드 캐시 / 원격 캐시

- 콘텐츠 해시 기반 캐시 무효화 (mtime이 아니라 내용 기준 — fresh checkout에서도 캐시 재사용 검증됨)
- 공유/원격 캐시 디렉토리 (두 머신 간 검증됨) — C/C++, Java 대상
- 다른 언어(Go/Rust/JS 등)는 캐시 대상에 안 들어가 있는 걸로 보임 → 코드 확인 결과 build cache는 cache.py/remote_cache.py가 C/C++/Java 어댑터에서만 호출됨. **홍보 문구에서 "빌드 캐시"를 언어 제한 없이 말하면 과장** — C/C++/Java 한정이라고 명시하는 게 정확함.

## 7. Pre/Post-build 훅

`stoke.toml`의 타겟마다 `pre_build`/`post_build` 셸 커맨드 리스트. `build`/`build --all`/`watch`/`hot-reload` 전 경로에서 동작, 실패 시 즉시 중단. 구현이 20줄 남짓으로 단순 (hooks.py) — 셸 커맨드를 그대로 `subprocess.run(shell=True)`로 실행하는 방식이라 강력하지만, stoke.toml에 임의 커맨드를 넣을 수 있다는 뜻. **(2026-08-29 반영)** README.md·README_ko.md·website/docs/configuration/stoke-toml.md·faq.md에 "신뢰 안 되는 저장소를 clone해서 바로 build하지 말라"는 보안 고지를 명시적으로 추가함.

## 5-1. Private Registry / Mirror

Sonatype Nexus 기준 실증(raw 리포 + maven-central 프록시, Basic Auth 포함). 툴체인 설치 + Java 의존성 다운로드 양쪽 다 미러 지정 가능. 폐쇄망 기업 대상 홍보 포인트로 강함.

## 8. IDE 연동

`stoke ide-sync` — VSCode/IntelliJ/Eclipse 설정 자동 생성. 최근 커밋(`0647883`)에서 "VSCode settings.json 데이터 손실 버그"를 고친 이력 있음 — 기존 설정을 덮어쓰지 않도록 막 고친 상태라, 홍보 전에 한 번 더 실사용 테스트해보는 걸 권장.

## 9. 플러그인 시스템

`stoke.languages` / `stoke.frameworks` entry point로 외부 pip 패키지가 언어나 `init` 스캐폴드를 추가 가능. stoke 소스를 건드릴 필요 없음. 독립 예제 패키지로 검증됨.

- **한계**: 플러그인 언어는 `stoke init`의 대화형 마법사 진입점이 자동으로 안 생김 — 플러그인이 자기 `stoke.frameworks` entry point를 따로 등록해야 `init`으로 진입 가능. 확장성은 있지만 매끄럽진 않음.

## 10. Reproducible builds (lock 파일)

`lock_mode = "commit"`(기본, 커밋해서 팀 공유) 또는 `"local"`. lock.py가 262줄로 실제 구현 있음.

---

## 필요 없어 보이거나 홍보 시 주의할 부분

1. **"빌드 캐시"를 전체 언어 기능처럼 홍보하지 말 것** — 실제로는 C/C++/Java 전용. Go/Rust/TS 등에는 캐시가 없음.
2. **Rust/Kotlin/C#/Ruby/PHP는 "지원"이라고만 하고 "검증됨"이라고 하지 말 것** — 코드 경로는 있지만 대규모 실전 프로젝트에서 검증 안 됐다고 FEATURES.md에 스스로 적어둠. 과장하면 나중에 이슈로 돌아옴.
3. ~~macOS/Linux는 아직 pip 설치만 되고 미검증~~ — **해결됨 (2026-08-29)**: `.github/workflows/release.yml`이 태그 push 시 Windows exe와 함께 macOS/Linux 네이티브 tarball도 빌드해서 Release에 올림. pip 설치 경로는 완전히 제거함(README 등 전체 문서 갱신).
4. **Rails/Laravel 미지원은 버그 아님, 설계 결정** — "Ruby/PHP 지원"이라고만 쓰면 사용자가 Rails 기대하다 실망할 수 있음. Sinatra/Slim이라고 구체적으로 써야 함.
5. **`stoke install <tool>`의 `tool` 인자가 사실상 `vcpkg` 하나뿐** (`choices=["vcpkg"]`) — CLI 형태상 여러 툴을 설치할 수 있을 것처럼 보이지만 실제로는 vcpkg 전용. 나머지는 전부 `--language` 플래그로 감. 향후 다른 tool이 추가되지 않는 한 이 서브커맨드 형태(`install vcpkg`)와 `--language` 형태가 공존하는 게 다소 일관성이 없어 보임 — API 설계상 정리 대상이지 지금 당장 없앨 기능은 아님.
6. ~~pre/post-build 훅은 임의 셸 실행이라 보안 고지가 필요~~ — **해결됨 (2026-08-29)**: README/README_ko/설정 레퍼런스/FAQ에 "신뢰 안 되는 저장소를 clone해서 바로 build하지 말라"는 경고 문구 추가.
7. ~~inter-target 의존성 그래프 없음~~ — **해결됨 (2026-08-29)**: `depends_on` 필드 추가 (config.py, depgraph.py). `stoke build`/`build --all`이 의존성부터 순서대로 빌드, 순환/미존재 타겟 참조는 로드 시점에 에러, 의존성 실패 시 그 타겟에 의존하는 타겟은 스킵. 실제 스모크 테스트로 체인 빌드/실패 전파/순환 검출/미존재 타겟 검출까지 확인함.
8. ~~CMake/Meson 통합 없음~~ — **CMake는 해결됨 (2026-08-29)**: `build_system = "cmake"`로 기존 CMakeLists.txt 프로젝트에 위임 가능 (cmake_adapter.py). Windows MSVC/Visual Studio generator로 build/run/force-rebuild/clean 전부 실제 실행해서 확인함. **Meson은 여전히 미지원** — "CMake 프로젝트도 그대로 붙는다"는 정확하지만 "빌드 시스템 전반을 지원한다"고 뭉뚱그리면 안 됨.

## 결론

기능 목록 자체는 코드와 거의 일치하고 죽은 코드나 미사용 기능은 없음 — 오히려 최근 커밋(`2a4b7a8`)에서 실제로 안 쓰는 `go_version` 설정 필드를 스스로 제거한 이력이 있을 정도로 정리가 잘 돼 있음. 홍보에서 조심할 부분은 "기능이 쓸모없다"가 아니라 **검증 범위를 실제보다 넓게 말하지 않는 것**(캐시 언어 범위, 신규 5개 언어의 실전 검증 여부, Rails/Laravel 부재, CMake 경로에서 무시되는 필드).

2026-08-29 기준 남은 항목: 5(install vcpkg API 비일관성), 8의 Meson 미지원. 나머지는 전부 해결됨.
