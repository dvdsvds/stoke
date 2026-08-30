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

- `stoke install <python|java|c|cpp|go|nodejs|rust|csharp|ruby|php> [--version] [--list] [--base-url]` (`--language=`는 하위 호환용으로 남아있음) — 버전 매니저 없이 stoke가 직접 설치. **정정 (2026-08-30)**: 이전 버전의 이 문서는 "Rust/Kotlin/C#/Ruby/PHP는 자체 설치 도구로 위임(직접 설치 미지원)"이라고 적어뒀는데, `website/docs/versions/*.json`을 실제로 확인해보니 rust/csharp/ruby/php는 전부 실제 다운로드 URL이 있는 정식 버전 소스가 있고 `install_lang.py`가 그대로 설치함 — 확인 없이 옮겨 적은 이전 기록이 틀렸음. **Kotlin만 진짜로 별도 설치가 없음** — `SUPPORTED_LANGUAGES`엔 들어있지만 `kotlin.json`이 없어서 `stoke install kotlin`을 치면 raw `HTTP 404` 에러로 죽던 버그가 있었음(2026-08-30에 발견/수정, 아래 참고).
- `stoke uninstall <language> | vcpkg`
- `--base-url` / `STOKE_VERSION_API_BASE`로 사내 미러 서버 지정 가능 (폐쇄망 대응)

## 4. C/C++ 전용 기능

- `stoke vcpkg install/remove/list/version`, `stoke install vcpkg` — vcpkg 라이브러리 매니저 연동
- 빌드 프로파일(`[profiles.*]`) — debug/release 기본 제공 + 커스텀 프로파일, `compiler = "msvc"`로 Windows에서 MSVC 지정 가능 (gcc/clang과 나란히)
- `build_system = "cmake"` (2026-08-29 추가) — 이미 `CMakeLists.txt`가 있는 C/C++ 타겟은 stoke 자체 컴파일 모델 대신 cmake configure/build로 위임. `build`/`run`/`watch`/`hot-reload`/`clean` 전부 그대로 씀. c_standard/profile 필드는 이 경로에서 무시됨(CMakeLists.txt가 관리) — 홍보에서 "기존 CMake 프로젝트도 그대로 붙는다"는 정확하지만, "표준/컴파일 플래그도 stoke.toml로 관리된다"는 이 경로에서는 틀림.
- `build_system = "meson"` (2026-08-30 추가) — 같은 구조로 `meson.build`가 있는 C/C++ 타겟을 meson setup + `meson compile`(ninja 백엔드)로 위임. `stoke build`(디버그/릴리스/--force 전부), `stoke run`, `stoke clean` 실제로 meson+ninja를 설치해서 end-to-end 스모크 테스트함(재빌드 시 재설정 스킵하고 ninja no-op 확인, --force는 빌드 디렉토리 삭제 후 재설정 확인). `watch`/`hot-reload`는 CMake 경로와 동일하게 `make_adapter()`를 통해 자연히 지원되지만 별도로 실행 검증은 안 함. cmake 경로와 마찬가지로 c_standard/profile 필드는 meson.build가 관리하므로 무시됨.

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
5. ~~`stoke install <tool>`의 `tool` 인자가 사실상 `vcpkg` 하나뿐~~ — **해결됨 (2026-08-30)**: positional `tool` 인자가 `vcpkg`뿐 아니라 `SUPPORTED_LANGUAGES`(python/java/c/cpp/conda/go/nodejs/rust/kotlin/csharp/ruby/php)도 받도록 확장함. 이제 `stoke install python`처럼 `stoke vcpkg install <library>`와 같은 패턴으로 씀. 기존 `stoke install --language=X`는 하위 호환으로 계속 동작(내부적으로 `--language`가 우선순위를 가짐), `--help` 문구에 "deprecated, use the positional argument instead"라고 안내. `install_lang.py`의 언어 목록이 세 곳에 중복돼 있던 것도 `SUPPORTED_LANGUAGES` 상수 하나로 통합.
6. ~~pre/post-build 훅은 임의 셸 실행이라 보안 고지가 필요~~ — **해결됨 (2026-08-29)**: README/README_ko/설정 레퍼런스/FAQ에 "신뢰 안 되는 저장소를 clone해서 바로 build하지 말라"는 경고 문구 추가.
7. ~~inter-target 의존성 그래프 없음~~ — **해결됨 (2026-08-29)**: `depends_on` 필드 추가 (config.py, depgraph.py). `stoke build`/`build --all`이 의존성부터 순서대로 빌드, 순환/미존재 타겟 참조는 로드 시점에 에러, 의존성 실패 시 그 타겟에 의존하는 타겟은 스킵. 실제 스모크 테스트로 체인 빌드/실패 전파/순환 검출/미존재 타겟 검출까지 확인함.
8. ~~CMake/Meson 통합 없음~~ — **둘 다 해결됨.** CMake(2026-08-29): `build_system = "cmake"`로 기존 CMakeLists.txt 프로젝트에 위임 가능 (cmake_adapter.py). Windows MSVC/Visual Studio generator로 build/run/force-rebuild/clean 전부 실제 실행해서 확인함. Meson(2026-08-30): `build_system = "meson"`으로 기존 meson.build 프로젝트에 위임 가능 (meson_adapter.py). meson+ninja 실제 설치해서 build/run/force-rebuild/clean 확인함.

## 결론

기능 목록 자체는 코드와 거의 일치하고 죽은 코드나 미사용 기능은 없음 — 오히려 최근 커밋(`2a4b7a8`)에서 실제로 안 쓰는 `go_version` 설정 필드를 스스로 제거한 이력이 있을 정도로 정리가 잘 돼 있음. 홍보에서 조심할 부분은 "기능이 쓸모없다"가 아니라 **검증 범위를 실제보다 넓게 말하지 않는 것**(캐시 언어 범위, 신규 5개 언어의 실전 검증 여부, Rails/Laravel 부재, CMake/Meson 경로에서 무시되는 필드).

2026-08-30 기준: 이 문서에 남아있던 항목(5. install API 비일관성, 8. Meson 미지원) 전부 해결됨.

## 새 기능: stoke test, stoke add/remove, kotlin install 버그 (2026-08-30)

사용자가 "stoke 기능에 개선점 없나" 물어봐서 코드 훑다가 나온 3개 항목, 전부 처리함.

- **`stoke test [target] [--debug|--release|--profile] [-v]`** — 이전엔 build/run/watch/hot-reload/clean만 있고 테스트 실행이 아예 없었음(가장 큰 구멍으로 판단해서 1순위 제안했었음). 언어별로 그 생태계의 표준 테스트 도구에 위임:
  - python: venv에 pytest 있으면 `pytest`, 없으면 stdlib `unittest discover`
  - go: `go test ./...`, rust: `cargo test`, csharp: `dotnet test`
  - kotlin: `gradle test`(빌드에서 `-x test`로 빼뒀던 그 태스크를 여기서 돎)
  - javascript/typescript: package.json의 `scripts.test`를 `npm test`로
  - ruby: spec/ 있으면 rspec, 아니면 Rakefile의 test 태스크
  - php: `vendor/bin/phpunit` (없으면 설치 안내)
  - C/C++ build_system="cmake": `ctest --test-dir ... --output-on-failure`
  - C/C++ build_system="meson": `meson test -C ...`
  - java, C/C++ 네이티브 빌드는 처음엔 미지원으로 남겼다가 (2026-08-30, 사용자가 "그럼 프레임워크 추가하자"고 해서) **바로 이어서 둘 다 구현함** — 아래 참고.
  - python/go 조합은 실제 pytest/go test 설치해서 end-to-end 스모크 테스트함(둘 다 통과 확인).

- **java `stoke test` — JUnit 5 (JUnit Platform Console Standalone)**: stoke의 java 빌드가 순수 javac 직접 호출 모델이라(Maven/Gradle 없음) 테스트 프레임워크가 아예 없었음. `org.junit.platform:junit-platform-console-standalone:1.11.3` 하나(JUnit Jupiter API+엔진까지 다 들어있는 uber jar)를 Maven Central에서 받아서(기존 `maven.py`의 `download_jar`/`MavenCoordinate` 재사용) `.stoke/java/<target>/test-deps/`에 캐싱. 새 `test_sources` stoke.toml 필드(java_adapter가 `.java` 파일만 수집)로 테스트 파일 지정 → `.stoke/java/<target>/test-classes/`에 컴파일(메인 classes_dir + deps + junit jar가 classpath) → `java -jar <junit jar> execute --classpath ... --scan-classpath <test-classes> --disable-banner`로 실행. 사용자는 표준 `org.junit.jupiter.api.Test`/`Assertions`를 그대로 씀 — stoke 전용 assertion 문법 없음. 실제 JDK로 컴파일+실행해서 통과/실패 케이스(각각 exit 0/1) 둘 다 end-to-end 검증함.

- **C++ `stoke test` — doctest (헤더 하나, stoke 패키지에 번들)**: [doctest](https://github.com/doctest/doctest) v2.4.11 `doctest.h`(MIT 라이선스, 라이선스 헤더 그대로 유지)를 `src/stoke/languages/c/vendor/doctest.h`로 번들함(네트워크 다운로드 불필요) — `pyproject.toml`의 `[tool.setuptools.package-data]`와 `stoke.spec`의 `datas`에 둘 다 등록해서 pip 설치판과 PyInstaller exe 양쪽에 실제로 포함되게 함. `test_sources`(cpp만) 글롭으로 테스트 파일 지정 → main()이 없는 나머지 소스(라이브러리 코드, 정규식으로 감지)와 같이 컴파일 → stoke가 자동 생성한 `_stoke_doctest_main.cpp`(`DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN`)로 링크해서 `test_runner.exe` 생성 후 실행. **plain C는 여전히 미지원**(doctest는 C++ 전용이라 — Unity 같은 C 프레임워크는 자동 디스커버리를 위해 테스트 함수 시그니처를 파싱해서 `RUN_TEST()` 호출부를 생성해야 해서 doctest/JUnit보다 작업량이 꽤 더 필요함, 이번 라운드에서 명시적으로 스코프 아웃함 — `stoke test`가 plain C 타겟에서 이 이유를 설명하는 에러를 냄). 실제 g++로 컴파일+링크해서 통과/실패 케이스(각각 exit 0/1) 둘 다 end-to-end 검증함(PowerShell에서 직접 확인 — Git Bash/MSYS2 서브프로세스 실행 시 exit 127로 잘못 보이는 환경 문제가 있었는데 이건 테스트 하네스 쪽 문제였고 실제 stoke 동작과는 무관함을 확인함).

- **`stoke add <package> [version] [--target=X]` / `stoke remove <package> [--target=X]`** — python/java에서 stoke.toml의 `[targets.X.deps]`에 패키지 추가+즉시 설치(`add`는 내부적으로 `stoke build` 재사용)/제거. 다른 언어는 대상에서 뺌 — go/rust/kotlin/csharp/ruby/php/js/ts는 stoke.toml이 의존성 매니페스트가 아니라 각자 네이티브 파일(go.mod, Cargo.toml 등)이 매니페스트라 이미 `cargo add`/`npm install`/`go get` 등을 그대로 쓰는 게 맞음(README에 이미 명시된 설계 원칙) — 대신 시도하면 어떤 네이티브 명령어를 쓰라는 안내를 띄움. C/C++은 이미 `stoke vcpkg install/remove`가 같은 역할을 해서 제외. `toml_editor.add_dep`/`remove_dep`(기존에 vcpkg 명령어가 쓰던 것)을 그대로 재사용. python으로 실제 `stoke add requests` → 설치 확인 → `stoke remove requests` → 제거 확인까지 end-to-end 검증함.

- **`stoke install kotlin` 실제 버그 발견/수정**: `SUPPORTED_LANGUAGES`엔 kotlin이 들어있는데 `website/docs/versions/kotlin.json`이 없어서 `fetch_versions()`가 raw `HTTP 404 Not Found`로 죽었음 — 사용자 입장에선 원인을 알 수 없는 에러. `_NO_DIRECT_INSTALL` 딕셔너리로 kotlin만 먼저 걸러서 "Kotlin은 별도 툴체인이 없고 JDK+Gradle로 빌드되니 `stoke install java`를 쓰라"는 명확한 안내로 바꿈. **이 과정에서 이전 기록(위 참고)이 rust/csharp/ruby/php를 "위임"이라고 잘못 적어놨던 것도 같이 정정함** — 실제로는 이 4개 다 `website/docs/versions/*.json`에 진짜 다운로드 URL이 있고 stoke가 직접 설치함. README.md/README_ko.md도 같이 고침.

- **부수적으로 잡은 버그**: `cli/deps.py`의 `cmd_remove_dep` 안내 메시지에 em dash(—)를 그대로 썼다가 Windows cp949 콘솔에서 stdout에 UnicodeEncodeError로 죽는 걸 실제로 재현함 (stderr는 기본 errors="backslashreplace"라 안 죽지만 stdout은 "strict"라 죽음). ASCII 하이픈으로 교체.

## 추가로 발견된 버그 (2026-08-30, 사용자 질문 계기)

**`stoke c list`/`stoke cpp list`가 `stoke install`로 받은 프로젝트 로컬 gcc/g++를 안 보여줬음.** `python`/`java`의 `detect_all(project_root)`는 `.stoke/toolchains`를 최우선으로 스캔하는데, `c`/`cpp`의 `detect_all()`은 애초에 `project_root` 매개변수가 없어서 시스템 PATH의 gcc/clang/MSVC만 봤음 — `_detect_local()`이라는 관련 함수가 이미 있었지만 `find_compiler()`(빌드용, 버전 하나만 찾음)에서만 쓰이고 `detect_all`엔 연결이 안 돼 있었음.

수정: `_detect_local()`을 전체 목록을 반환하는 `_detect_local_all()`로 확장하고(기존 `_detect_local`은 `_detect_local_all()[0]`으로 재구현, `find_compiler` 동작은 그대로 유지), `detect_all(project_root=None)`이 `project_root`를 받으면 로컬 설치를 시스템 설치보다 먼저 포함하도록 수정. `cli/tools.py`의 `cmd_c_list`/`cmd_cpp_list`가 `_current_project_root()`를 넘기도록 변경. 프로젝트 로컬에 실제 gcc 바이너리를 복사해 넣고 `stoke cpp list` 실행까지 end-to-end로 재현/검증함.
