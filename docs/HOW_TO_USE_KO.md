# stoke — 사용 가이드 (v1.5.1)

실제로 어떻게 쓰면 되는지, 어떤 상황에 맞는지, 상황별로 바로 쓸 수 있는 명령어를 정리한 문서.

## 요약

```bash
mkdir myapp && cd myapp
stoke init      # 언어 고르고 몇 가지 질문에 답하면 끝
stoke build     # 컴파일/준비
stoke run       # 실행
```

프로젝트당 `stoke.toml` 하나, 타겟도 하나(빌드 타겟이 여러 개 필요하면 8번 섹션 참고). 12개 언어의 build/run/watch/scaffold를 CLI 하나로. `stoke init`이 초기 파일을 만들어주고, 그 외 설정(`include_dirs`, `pre_build`/`post_build`, 커스텀 `[profiles.*]` 등)은 직접 손으로 편집함.

---

## 1. 내 프로젝트에 stoke가 맞나?

**잘 맞는 경우:**
- 소규모~중규모 프로젝트, 팀 규모 대략 10~30명 정도.
- 12개 지원 언어 중 하나로 만든 서비스/앱 하나가 있고, 언어별 도구를 따로 익히는 대신 `build`/`run`/`watch` 명령어를 통일하고 싶은 경우.
- 팀원이 자주 합류하는데 위키 페이지에 적힌 수동 셋업 절차를 `stoke init --language=... --yes` 한 줄로 대체하고 싶은 경우.
- 무거운 도구(Bazel, Nx, Turborepo)를 도입하고 그 러닝커브를 감당하지 않고도 재현 가능한 빌드(커밋된 lock 파일)를 원하는 경우.
- 언어별로 이미 특정 툴체인(Cargo, Gradle, `dotnet`, Bundler, Composer, npm, Maven Central)을 쓰고 있는 환경 — stoke는 의존성 해결을 새로 만들지 않고 그대로 위임하므로 `Cargo.toml`/`build.gradle.kts` 등을 평소처럼 그대로 씀.

**잘 안 맞는 경우 (8번 섹션에 전체 목록):**
- CMake/Meson 위임 범위를 넘어서는 코드생성 빌드 그래프가 필요한 대규모 C/C++ 코드베이스 (CMake·Meson 프로젝트는 `build_system = "cmake"`/`"meson"`으로 지원 — 8번 섹션 참고).
- MSVC가 필요한 Windows 네이티브 C++ 환경 (stoke는 gcc/clang만 씀).
- stoke 자체 소스코드를 고치지 않고 사내 전용 언어/프레임워크 템플릿을 추가하는 플러그인 시스템이 필요한 팀.

---

## 2. 설치

**Windows** — 네이티브 설치 프로그램, Python 포함, 별도 사전 준비 필요 없음:
[Releases 페이지](https://github.com/dvdsvds/stoke/releases/latest)에서 다운로드.

**Linux/macOS** — 네이티브 tarball, Python 포함, 별도 사전 준비 필요 없음:
[Releases 페이지](https://github.com/dvdsvds/stoke/releases/latest)에서 `stoke-X.Y.Z-<platform>-<arch>.tar.gz` 다운로드 후 압축 풀고 `PATH`에 추가:
```bash
tar xzf stoke-*.tar.gz
export PATH="$PWD/stoke:$PATH"
```
서명은 안 돼 있어서 macOS는 처음 실행 시 Gatekeeper가 막음 — `stoke` 실행 파일을 우클릭 → "열기"로 한 번만 허용하면 됨.

---

## 3. 첫 프로젝트 만들기

```bash
mkdir myapp && cd myapp
stoke init
```

프로젝트 이름 → 언어 → 언어별 질문(Python 버전, Java 버전, C/C++ 표준, 선택적 툴체인 pin 등) → lock 모드(`commit` 또는 `local`) 순으로 진행됨. `stoke.toml`과 예시 소스 파일이 생성됨.

```bash
stoke build      # 컴파일/준비
stoke run        # 실행
stoke watch       # 파일 바뀌면 자동으로 다시 빌드
```

**뭘 원하는지 이미 알고 있거나, 스크립트(CI, 온보딩)로 자동화하고 싶으면** 프롬프트 다 건너뛰기:

```bash
stoke init --language=python --name=myapp --version=3.12 --lock-mode=commit --yes
```

**언어만 고르지 않고 알려진 프레임워크로 바로 스캐폴딩:**

```bash
stoke init fastapi        # 또는: flask, django, spring-boot, gin, echo, fiber, chi,
                           # bubbletea, actix-web, axum, rocket, ktor, spring-boot-kotlin,
                           # aspnet-core, sinatra, slim, express, fastify,
                           # nextjs, nestjs, vite, nuxt, sveltekit, hono
```

---

## 4. 언어별 치트시트

| 언어 | `stoke init --language=` | 내부적으로 쓰는 빌드 도구 | 버전 pin | 의존성 |
| --- | --- | --- | --- | --- |
| Python | `python` | pip / venv / conda | `stoke.toml`의 `python_version` | stoke 자체 lock (`stoke.lock`) |
| Java | `java` | `javac` 직접 | `stoke.toml`의 `java_version` | stoke 자체 lock, jar는 Maven Central |
| C | `c` | gcc/clang | `stoke.toml`의 `c_standard` | vcpkg |
| C++ | `cpp` | gcc/clang | `stoke.toml`의 `cpp_standard` | vcpkg |
| Go | `go` | `go build`/`go run` | 없음 | `go.sum` |
| Rust | `rust` | `cargo build --release`/run | 선택적 `rust-toolchain.toml` | `Cargo.lock` |
| Kotlin | `kotlin` | Gradle (`gradlew` 또는 시스템 `gradle`) | `java_version` (`-Dorg.gradle.java.home`로 강제) | Gradle 자체 해석 |
| C# | `csharp` | `dotnet build`/`dotnet run` | 선택적 `global.json` | NuGet (`dotnet`이 처리) |
| Ruby | `ruby` | Bundler + `ruby` | 선택적 `.ruby-version` | `Gemfile.lock` |
| PHP | `php` | Composer + `php` | 선택적 `composer.json`의 `require.php` | `composer.lock` |
| JavaScript | `javascript` | Node.js (`npm install` + `node`) | 없음 | `package-lock.json` |
| TypeScript | `typescript` | Node.js + tsx | 없음 | `package-lock.json` |

`stoke install --language=<lang> --version=<v>`로 올바른 버전이 없으면 툴체인(Python/Java/gcc/Go/Node.js)을 설치함:

```bash
stoke install --language=python --version=3.12
stoke install --language=python --list        # 설치 가능한 버전 목록
stoke uninstall --language=python --version=3.12
```

C/C++ 의존성은 vcpkg로:

```bash
stoke install vcpkg                    # 최초 1회 설치
stoke vcpkg install fmt --target=myapp
stoke vcpkg list --target=myapp
stoke vcpkg remove fmt --target=myapp
```

---

## 5. 자주 쓰는 명령어

```bash
stoke build [target] [--force]        # --force는 캐시 무시하고 전부 다시 컴파일
stoke run [target]
stoke watch [target]                  # 파일 바뀌면 자동 재빌드
stoke hot-reload [target]             # 재빌드 + 실행 중인 프로세스 자동 재시작
stoke clean [target] [--all]          # 빌드 산출물 삭제, --all이면 lock 파일도 같이 삭제
stoke ide-sync                        # VSCode/Eclipse/IntelliJ 설정 파일 재생성
stoke exec [--target=X] -- <command>  # 타겟의 프로젝트 로컬 툴체인을 PATH에 얹은 채로 명령 실행
```

**`stoke exec`** — `stoke install`/`stoke init`은 언어 툴체인을 시스템 PATH를 안 건드리고 `.stoke/toolchains/`에만 설치하므로, 그 언어가 시스템에 전혀 없어도 `stoke build`/`run`은 잘 됩니다. 하지만 사용자가 직접 치는 네이티브 도구 명령(`go mod tidy`, `cargo add serde`, `bundle add rails`, `composer require monolog/monolog`, `dotnet add package Newtonsoft.Json`)은 PATH만 보기 때문에, 그 언어가 프로젝트 로컬로만 설치돼 있으면 실패합니다. `stoke exec`는 그 프로젝트 로컬 툴체인의 `bin/`을 PATH 맨 앞에 얹은(Rust는 `RUSTUP_HOME`/`CARGO_HOME`도 같이 설정) 상태로 명령을 대신 실행해줍니다:

```bash
stoke exec -- go mod tidy
stoke exec --target=api -- cargo add serde
```

`stoke init`에서 Python/Java/C/C++ 프로젝트는 어떤 IDE와 연동할지 물어봅니다 (`vscode`가 기본값이고 `.vscode/settings.json` + C/C++는 `compile_commands.json`/`c_cpp_properties.json`도 씀, `eclipse`는 Java용 `.classpath`/`.project`, `intellij`는 Java용 `pom.xml` 또는 C/C++용 `compile_commands.json`만 (CLion, clangd, clangd 기반 Vim/Neovim/Emacs 설정도 이 파일을 직접 읽음), `none`은 `stoke build`할 때 아무 파일도 안 씀). `stoke.toml`의 `[project]`에 `ide = "..."`로 저장되고 직접 수정해도 됩니다. 위에서 설명한 `stoke ide-sync`는 이거랑 별개로, 이 설정과 무관하게 찾은 모든 stoke 프로젝트를 묶는 VSCode 멀티루트 워크스페이스 파일을 항상 만듭니다.

**빌드 프로파일 (C/C++ 전용):**

```bash
stoke build --debug          # 기본값
stoke build --release
stoke build --profile=asan   # stoke.toml에 [profiles.asan]을 정의해뒀다면
```

`stoke watch`/`stoke run`/`stoke hot-reload`도 같은 `--debug`/`--release`/`--profile` 플래그를 받음. 다른 언어는 무시함(빌드 프로파일 개념 자체가 없음).

---

## 6. 팀에서 쓸 때

### 6.1 한 줄 온보딩

수동 셋업 절차 페이지 대신 README나 셋업 스크립트에 이거 하나만:

```bash
stoke init --language=java --name=payments --version=21 --lock-mode=commit --yes
```

각 플래그는 대화형 마법사가 물어보는 질문과 1:1로 대응됨. `--yes`를 안 주면 기존 `stoke.toml`을 조용히 덮어쓰는 대신 큰 소리로 실패함(0이 아닌 종료 코드).

### 6.2 "내 컴퓨터에서는 되는데" 방지용 툴체인 버전 pin

| 언어 | 파일 | 누가 읽는지 |
| --- | --- | --- |
| Python/Java | `stoke.toml`의 `python_version`/`java_version` | stoke 자체, 빌드 시점에 확인 |
| C/C++ | `stoke.toml`의 `c_standard`/`cpp_standard` | stoke 자체 |
| Kotlin | `stoke.toml`의 `java_version` | stoke, `-Dorg.gradle.java.home`으로 강제 |
| Rust | `rust-toolchain.toml` | rustup, 자동으로 |
| C# | `global.json` | dotnet CLI, 자동으로 |
| Ruby | `.ruby-version` | rbenv/rvm/asdf/chruby, 자동으로 |
| PHP | `composer.json`의 `require.php` | Composer, `composer install` 시 강제 |

Go/JavaScript/TypeScript는 아직 pin 메커니즘이 없음 — 필요하면 `go.mod`의 `go` 지시자 / `package.json`의 `engines` + 자체 CI 체크에 의존할 것.

### 6.3 재현 가능한 빌드

`lock_mode = "commit"`(‎`stoke init`의 기본값)으로 두면 lock 파일이 프로젝트 루트에 생기고 git에 커밋됨 — 팀원과 CI 러너 전부 정확히 같은 의존성 버전으로 해석함. `lock_mode = "local"`은 대신 `.stoke/` 밑 gitignore 대상으로 두고, 개발자마다 다른 버전을 쓸 수 있게 함.

### 6.4 빌드 속도 — 캐시와 병렬화

**로컬 캐시**는 자동이고 콘텐츠 해시 기반임 (내용이 똑같은 파일이면 mtime이 바뀌어도 — 예: 새로 `git checkout`한 직후 — 재컴파일 안 함).

**공유/원격 캐시**는 C/C++와 Java에서, 팀 전체나 CI 전체가 같은 네트워크 공유 경로/NAS를 가리키게 하면:

```bash
export STOKE_REMOTE_CACHE_DIR=/mnt/shared/stoke-cache      # Windows면 매핑된 네트워크 드라이브도 가능
stoke build
```

한 머신이 뭔가 컴파일하면 공유 캐시에 채워지고, 같은 env var가 설정된 다른 머신/CI 러너가 같은 소스로 빌드하면 재컴파일 대신 캐시 히트를 받음. 별도 캐시 서버를 돌릴 필요 없음 — 그냥 디렉토리 하나임. Fail-open 방식: 접근 안 되거나 잘못 설정된 디렉토리는 조용히 로컬 컴파일로 넘어감, 빌드를 절대 깨뜨리지 않음.

**공유 네트워크 드라이브가 없는 원격 팀/클라우드 CI** — 대신 HTTP 캐시 서버를 가리키면 됨:

```bash
export STOKE_REMOTE_CACHE_URL=https://cache.mycompany.com
export STOKE_REMOTE_CACHE_USER=ci       # 선택, HTTP Basic Auth
export STOKE_REMOTE_CACHE_PASSWORD=***
stoke build
```

캐시 키도 동일하고 fail-open 동작도 동일함(서버가 안 되거나 잘못 설정됐거나 업로드가 실패해도 그냥 로컬 컴파일로 넘어감) — 공유 파일시스템이 없는 팀(원격 근무자, GitHub 호스팅 CI 러너 등)을 위한 `STOKE_REMOTE_CACHE_DIR`의 대체제. 둘 다 설정돼 있으면 `STOKE_REMOTE_CACHE_URL`이 우선함. 서버는 stoke가 보내는 바이트를 `/objects/<key>`, `/dirs/<key>.tar`에서 `GET`/`PUT`으로 응답하기만 하면 됨 — stoke 자체는 서버 구현체를 제공하지 않음.

**파일 단위 병렬 컴파일** (C/C++만 해당): 한 타겟 안의 소스 파일 여러 개가 자동으로 병렬 컴파일됨. `stoke.toml`에 `project.jobs`가 설정돼 있으면 그걸로, 아니면 CPU 개수로 병렬 수 제한.

### 6.5 폐쇄망/사내망 환경

stoke가 나가는 네트워크 호출을 전부 공개 인터넷 대신 사내 미러로 돌리기:

```bash
# 툴체인 다운로드 (stoke install)
export STOKE_VERSION_API_BASE=https://internal-mirror.company.com/stoke-versions
# 또는 호출할 때마다: stoke install --language=python --version=3.12 --base-url=https://internal-mirror.company.com/stoke-versions

# Java 의존성 다운로드 (stoke build)
export STOKE_MAVEN_REPO_URL=https://internal-mirror.company.com/maven2

# 미러가 인증(HTTP Basic)을 요구하면:
export STOKE_VERSION_API_USER=ci
export STOKE_VERSION_API_PASSWORD=***
export STOKE_MAVEN_USER=ci
export STOKE_MAVEN_PASSWORD=***
```

실제 Sonatype Nexus 환경(익명/인증 둘 다)에 대고 검증됨. 다른 모든 언어의 의존성 관리는 이미 각자 생태계 자체의 미러/레지스트리 설정(`pip.conf`, `.npmrc`, `NuGet.config`, `.cargo/config.toml`, Bundler/Composer 설정, vcpkg 레지스트리)을 그대로 따르므로 stoke 쪽에서 따로 해줄 게 없음.

### 6.6 CI/CD

stoke는 Python이 내장된 단일 실행 파일로 배포되므로, CI 러너나 Docker 빌드 스테이지에 stoke 자체를 돌리기 위한 별도 언어 런타임을 미리 깔 필요가 없음 — release 압축 파일을 받아서 `PATH`에 얹기만 하면 `stoke build`/`stoke test`/`stoke audit`가 로컬과 똑같이 동작함.

- [`docs/ci/github-actions.yml`](./ci/github-actions.yml) — stoke 설치 후, `actions/cache`로 공유 빌드 캐시(6.4절)를 런 사이에 복원하고 build/test/audit 실행.
- [`docs/ci/Dockerfile`](./ci/Dockerfile) — 멀티스테이지 빌드: build 스테이지에서 stoke + pin된 언어 툴체인으로 컴파일하고, 런타임 이미지에는 빌드 결과물만 담음.

`stoke audit`는 태생적으로 CI 친화적 — 확정된 의존성에서 알려진 CVE가 발견되면 non-zero exit을 하므로, 필수 체크로 걸어두면 그 자체로 머지 게이트가 됨.

### 6.7 모노레포

`stoke.toml` 하나는 언어당 타겟 하나만 지원함 (lock 파일이 언어당 버전 슬롯 하나뿐이라 타겟마다 하나가 아님) — 그래서 같은 언어 서비스 2개를 한 파일에 넣으면 서로 lock 정보를 덮어씀. 대신 서비스마다 독립된 `stoke.toml`/`stoke.lock`을 가진 서브디렉토리로 두고, 워크스페이스 루트로 묶음:

```bash
mkdir my-company && cd my-company
stoke init --workspace --name=my-company   # 루트 stoke.toml: 언어/타겟 없이 members 목록만

stoke new backend -l python -V 3.12
stoke new worker  -l python -V 3.11        # backend랑 Python 버전 달라도 충돌 없음
stoke new frontend -l typescript
```

```
my-company/
├── stoke.toml           # [workspace] members = ["backend", "worker", "frontend"]
├── backend/
│   ├── stoke.toml        # 독립 설정, python_version = "3.12"
│   └── stoke.lock
├── worker/
│   ├── stoke.toml        # python_version = "3.11"
│   └── stoke.lock
└── frontend/
    └── stoke.toml
```

각 서비스는 독립 프로젝트처럼 그대로 빌드 — `cd backend && stoke build`. `stoke new`를 워크스페이스 루트 안에서 실행하면 새 서비스가 루트 `members`에 자동 등록되고, 워크스페이스 밖에서 실행하면 그냥 서브디렉토리만 생성함 (워크스페이스 무관).

루트에서 `stoke build --all`/`stoke test --all`로 멤버 전체를 순차적으로 빌드/테스트 — 각자 자기 서브디렉토리와 자기 `stoke.toml`로 실행됨. 하나가 실패해도 나머지는 계속 진행하고, 끝나면 어떤 멤버가 실패했는지 모아서 보여주고 하나라도 실패했으면 non-zero exit:

```bash
cd my-company
stoke build --all
# === backend ===
# Build complete: backend
#
# === worker ===
# Build complete: worker
#
# All 2 member(s) succeeded.
```

---

## 7. 상황별 추천 세팅

**혼자 하는 프로젝트/프로토타입:** `stoke init` 하고 `lock_mode=commit` 기본값 그대로, 미러링/캐시 env var는 신경 안 써도 됨. 그냥 `stoke build && stoke run`, 반복 작업할 땐 `stoke watch`.

**작은 팀, 단일 언어:** 위와 동일 + `stoke init --language=... --yes` 한 줄을 온보딩 문서에 넣고, 언어 버전을 pin해서 팀원들 툴체인이 다 맞게 함.

**여러 언어를 쓰는 모노레포 (서비스 몇 개, 언어 다양):** 서비스마다 자기만의 `stoke.toml`을 자기 디렉토리에 따로 두세요 — stoke는 프로젝트당 타겟 하나짜리 도구입니다.

**CI 파이프라인:** 저장소에 이미 `stoke.toml`이 있으니 비대화형 init은 관련 없지만, CI에서 `stoke build --force`(직전 실행의 체크아웃에서 온 오래된 캐시를 못 믿으니 force) + `STOKE_REMOTE_CACHE_DIR`을 영속 캐시 볼륨으로 지정하면 CI 전용 캐시 설정 없이도 실행 간 캐싱을 얻음 — 팀 공유 캐시와 같은 메커니즘.

**폐쇄망 대기업 환경:** `STOKE_VERSION_API_BASE`/`STOKE_MAVEN_REPO_URL`(미러가 인증을 요구하면 `_USER`/`_PASSWORD` 쌍도)을 CI 환경과 팀 전체 셸 프로필/온보딩 문서에 한 번만 설정. `lock_mode=commit`과 같이 쓰면 첫 `stoke build` 이후로는 의존성 해결 때문에 인터넷에 나갈 일이 아예 없어짐.

---

## 8. stoke를 안 쓰는 게 나은 경우

- CMake/Meson 위임 범위를 넘어서는 코드 생성, 복잡한 빌드 그래프가 필요한 대규모/복잡한 C 또는 C++ 빌드 — stoke 자체 C/C++ 모델은 의도적으로 단순함(gcc/clang 직접 호출 + 자체 헤더 추적). 이미 `CMakeLists.txt`나 `meson.build`가 있다면 그 타겟에 `build_system = "cmake"` 또는 `"meson"`을 지정하세요 — stoke가 컴파일러를 직접 돌리는 대신 `build`/`run`/`watch`/`hot-reload`/`clean`을 `cmake configure`/`--build` 또는 `meson setup`/`compile`로 위임합니다.
- MSVC가 꼭 필요한 Windows C++ 환경 — gcc/clang(MSYS2/MinGW 경유)만 지원됨.
- stoke 자체 소스코드를 안 건드리고 사내 전용 언어/프레임워크 템플릿을 추가하는 플러그인 시스템이 필요한 경우 — 아직 없음.
- 이미 Rust/Kotlin/C#/Ruby/PHP를 대규모로 깊게 쓰고 있는 경우 — 이 다섯은 가장 최근에 추가된 언어라 원래 7개 언어만큼 대규모 실전 코드베이스에서 검증되지 않음.
- 하나의 `stoke.toml`로 여러 빌드 타겟(예: 백엔드 + 워커)을 관리하고 싶은 경우 — stoke는 프로젝트당 타겟 하나만 지원함. 각각 자기만의 `stoke.toml`을 자기 디렉토리에 따로 두세요.

---

## 9. 트러블슈팅

- **Gradle(Kotlin)이 아예 시작도 안 되고, JDK 버전을 언급하는 알쏭달쏭한 에러가 남**: 시스템 기본 JDK가 쓰고 있는 Gradle 버전에 비해 너무 새/오래됐을 수 있음(예: Gradle 8.10은 JDK 25 위에서 안 돌아감). `gradle`/`gradlew` CLI 자체를 돌리기 위해서만 `JAVA_HOME`을 지원되는 JDK로 맞춰줄 것 — 이건 `stoke.toml`의 `java_version`(프로젝트 자체가 컴파일에 쓰는 JDK를 정함)과는 별개임.
- **print 문 하나 때문에 Windows에서 `UnicodeEncodeError`로 크래시남**: Windows 콘솔의 기본 코드페이지는 로케일에 따라 다르고(예: 한글 로케일이면 `cp949`) UTF-8보다 좁음 — em-dash, 스마트 따옴표 같은 non-ASCII 문자가 콘솔 출력에 들어가면 어떤 머신에서는 크래시나고 어떤 머신에서는 안 남. stoke를 직접 확장하고 있다면 `print()` 문에는 ASCII만 쓰거나, 우회책으로 `PYTHONIOENCODING=utf-8`을 설정하거나 `chcp 65001`을 먼저 실행할 것.
- **공유/원격 캐시 디렉토리가 도움이 안 됨**: `STOKE_REMOTE_CACHE_DIR`이 모든 머신에서 정확히 같은 경로(또는 동등하게 매핑된 경로)로 실제 접근 가능한지, 소스 내용이 바이트 단위로 동일한지 확인할 것 — 캐시 키가 콘텐츠 해시 기반이라 공백 하나만 달라도 미스로 처리되는 게 의도된 동작임.
- **`stoke install`/`stoke build`(Java)가 사내 미러에 대고 401로 실패함**: 맞는 `_USER`/`_PASSWORD` env var 쌍(`STOKE_VERSION_API_USER`/`PASSWORD` 또는 `STOKE_MAVEN_USER`/`PASSWORD`)을 설정할 것 — 에러 메시지가 어떤 걸 설정해야 하는지 알려줌.

