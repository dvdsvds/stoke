# stoke — 사용 가이드 (v1.5.0)

실제로 어떻게 쓰면 되는지, 어떤 상황에 맞는지, 상황별로 바로 쓸 수 있는 명령어를 정리한 문서.

## 요약

```bash
mkdir myapp && cd myapp
stoke init      # 언어 고르고 몇 가지 질문에 답하면 끝
stoke build     # 컴파일/준비
stoke run       # 실행
```

프로젝트당 `stoke.toml` 하나. 12개 언어의 build/run/watch/scaffold를 CLI 하나로. `stoke.toml`은 처음부터 끝까지 CLI로만 관리하게 설계됨 — 직접 손으로 고칠 필요 없음 (`stoke init`을 기존 프로젝트 안에서 다시 실행하면 TOML을 직접 편집하라고 하는 대신 타겟을 추가해줌).

---

## 1. 내 프로젝트에 stoke가 맞나?

**잘 맞는 경우:**
- 소규모~중규모 프로젝트, 팀 규모 대략 10~30명 정도.
- 서비스 하나, 또는 한 저장소 안에 서로 관련된 몇 개의 서비스/타겟(예: Python API + Go 워커 + 작은 CLI 도구)이 있고, 어떤 타겟을 만지든 `build`/`run`/`watch` 명령어를 통일하고 싶은 경우.
- 팀원이 자주 합류하는데 위키 페이지에 적힌 수동 셋업 절차를 `stoke init --language=... --yes` 한 줄로 대체하고 싶은 경우.
- 무거운 도구(Bazel, Nx, Turborepo)를 도입하고 그 러닝커브를 감당하지 않고도 재현 가능한 빌드(커밋된 lock 파일)를 원하는 경우.
- 언어별로 이미 특정 툴체인(Cargo, Gradle, `dotnet`, Bundler, Composer, npm, Maven Central)을 쓰고 있는 환경 — stoke는 의존성 해결을 새로 만들지 않고 그대로 위임하므로 `Cargo.toml`/`build.gradle.kts` 등을 평소처럼 그대로 씀.

**잘 안 맞는 경우 (9번 섹션에 전체 목록):**
- CMake나 복잡한/코드생성이 필요한 빌드 그래프가 필요한 대규모 C/C++ 코드베이스.
- MSVC가 필요한 Windows 네이티브 C++ 환경 (stoke는 gcc/clang만 씀).
- stoke 자체 소스코드를 고치지 않고 사내 전용 언어/프레임워크 템플릿을 추가하는 플러그인 시스템이 필요한 팀.
- 타겟 간에 진짜 빌드 순서 의존성이 있는 프로젝트(타겟 B가 타겟 A가 끝난 뒤에만 빌드돼야 함) — `stoke build --all`은 모든 타겟을 독립적이라고 가정하고, 의존성 그래프가 없음.

---

## 2. 설치

**Windows** — 네이티브 설치 프로그램, Python 포함, 별도 사전 준비 필요 없음:
[Releases 페이지](https://github.com/dvdsvds/stoke/releases/latest)에서 다운로드.

**Linux/macOS/Python 3.11+ 있는 곳 어디든:**
```bash
pip install stoke-build
```

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
                           # actix-web, axum, rocket, ktor, spring-boot-kotlin,
                           # aspnet-core, sinatra, slim, express, fastify,
                           # nextjs, nestjs, vite, nuxt, sveltekit, hono
```

---

## 4. 타겟 여러 개로 키우기

`stoke.toml`이 이미 있는 상태에서 `stoke init`을 다시 실행하면 **"이 프로젝트에 새 타겟 추가"** 옵션을 먼저 보여줌 — 덮어쓰기를 강제하지 않음. 프로젝트를 키우는 정식 방법이 이거고, `[targets.*]` 블록을 직접 손으로 `stoke.toml`에 써넣으면 안 됨.

```
$ stoke init
stoke.toml already exists at ./stoke.toml

What would you like to do?
  1. Add a new target to this project (default)
  2. Overwrite (start over with a new stoke.toml)
Select [1-2, default 1]: 1

Target name: worker
Language:
  1. Python (default)  2. Java  3. C  4. C++  5. Go  6. Rust
  7. Kotlin  8. C#  9. Ruby  10. PHP  11. JavaScript  12. TypeScript
Select [1-12, default 1]: 5

Added target 'worker' (go) to ./stoke.toml
Source files created under: ./worker
```

결과적으로 `stoke.toml` 하나에 `[targets.*]` 블록 여러 개가 생김 — 예를 들어 Python API와 Go 워커가 나란히:

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.api]
language = "python"
sources = ["api/src/main.py"]
entry = "api/src/main.py"
python_version = "3.12"

[targets.worker]
language = "go"
```

각각 독립적으로 빌드/실행하거나, 한꺼번에:

```bash
stoke build api
stoke build worker
stoke build --all      # stoke.toml의 모든 타겟을 병렬로 빌드
stoke run api
stoke run worker
```

**언어별로 두 번째 타겟이 어떻게 독립적으로 빌드되는지:**

| 언어 그룹 | 독립성이 어떻게 보장되는지 |
| --- | --- |
| Python, Java, C, C++, Ruby, PHP, JavaScript, TypeScript | `stoke.toml`의 `target.sources`/`target.entry`가 `<타겟이름>/` 밑 특정 파일들로 범위를 좁힘. |
| Go | 각 타겟이 루트 `go.mod` 하나를 공유하는 자기만의 패키지(Go 자체의 `cmd/api/`, `cmd/worker/` 관례). stoke가 모듈 전체 대신 `./<타겟이름>`을 빌드함. |
| Rust | 첫 번째 이후의 각 타겟이 Cargo **워크스페이스 멤버**(`<타겟이름>/Cargo.toml`)가 됨. 루트는 그대로 일반 패키지. stoke가 `--manifest-path`를 명시적으로 넘김. |
| Kotlin | 첫 번째 이후의 각 타겟이 Gradle **서브프로젝트**(`<타겟이름>/build.gradle.kts`, `settings.gradle.kts`에 `include()`로 등록)가 됨. stoke는 항상 콜론으로 명시된 태스크 경로(`:worker:build`)를 써서 한 타겟 빌드가 다른 타겟까지 건드리지 않게 함. |
| C# | 각 타겟이 `<타겟이름>/` 밑에 자기만의 `.csproj`를 가짐. stoke가 그 `.csproj` 경로를 `dotnet build`에 명시적으로 넘기고, 루트 `.csproj`가 새 타겟 폴더를 자기 컴파일 대상에 안 끌어들이도록 exclude 규칙도 patch함 (SDK 스타일 `.csproj`는 기본적으로 재귀적으로 glob하기 때문에 필요한 조치). |

Go/Rust/Kotlin/C# 네 언어 전부 이 문서를 만든 것과 같은 세션에서 이 기능을 지원하도록 고쳐졌음 — 더 예전 버전의 stoke를 쓰고 있다면 두 번째 Go/Rust/Kotlin/C# 타겟이 독립적으로 안 빌드될 수 있으니 먼저 업그레이드할 것.

---

## 5. 언어별 치트시트

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

## 6. 자주 쓰는 명령어

```bash
stoke build [target] [--force]        # --force는 캐시 무시하고 전부 다시 컴파일
stoke run [target]
stoke watch [target]                  # 파일 바뀌면 자동 재빌드
stoke hot-reload [target]             # 재빌드 + 실행 중인 프로세스 자동 재시작
stoke clean [target] [--all]          # 빌드 산출물 삭제, --all이면 lock 파일도 같이 삭제
stoke ide-sync                        # VSCode/Eclipse/IntelliJ 설정 파일 재생성
```

**빌드 프로파일 (C/C++ 전용):**

```bash
stoke build --debug          # 기본값
stoke build --release
stoke build --profile=asan   # stoke.toml에 [profiles.asan]을 정의해뒀다면
```

`stoke watch`/`stoke run`/`stoke hot-reload`도 같은 `--debug`/`--release`/`--profile` 플래그를 받음. 다른 언어는 무시함(빌드 프로파일 개념 자체가 없음).

---

## 7. 팀에서 쓸 때

### 7.1 한 줄 온보딩

수동 셋업 절차 페이지 대신 README나 셋업 스크립트에 이거 하나만:

```bash
stoke init --language=java --name=payments --version=21 --lock-mode=commit --yes
```

각 플래그는 대화형 마법사가 물어보는 질문과 1:1로 대응됨. `--yes`를 안 주면 기존 `stoke.toml`을 조용히 덮어쓰는 대신 큰 소리로 실패함(0이 아닌 종료 코드).

### 7.2 "내 컴퓨터에서는 되는데" 방지용 툴체인 버전 pin

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

### 7.3 재현 가능한 빌드

`lock_mode = "commit"`(‎`stoke init`의 기본값)으로 두면 lock 파일이 프로젝트 루트에 생기고 git에 커밋됨 — 팀원과 CI 러너 전부 정확히 같은 의존성 버전으로 해석함. `lock_mode = "local"`은 대신 `.stoke/` 밑 gitignore 대상으로 두고, 개발자마다 다른 버전을 쓸 수 있게 함.

### 7.4 빌드 속도 — 캐시와 병렬화

**로컬 캐시**는 자동이고 콘텐츠 해시 기반임 (내용이 똑같은 파일이면 mtime이 바뀌어도 — 예: 새로 `git checkout`한 직후 — 재컴파일 안 함).

**공유/원격 캐시**는 C/C++와 Java에서, 팀 전체나 CI 전체가 같은 네트워크 공유 경로/NAS를 가리키게 하면:

```bash
export STOKE_REMOTE_CACHE_DIR=/mnt/shared/stoke-cache      # Windows면 매핑된 네트워크 드라이브도 가능
stoke build
```

한 머신이 뭔가 컴파일하면 공유 캐시에 채워지고, 같은 env var가 설정된 다른 머신/CI 러너가 같은 소스로 빌드하면 재컴파일 대신 캐시 히트를 받음. 별도 캐시 서버를 돌릴 필요 없음 — 그냥 디렉토리 하나임. Fail-open 방식: 접근 안 되거나 잘못 설정된 디렉토리는 조용히 로컬 컴파일로 넘어감, 빌드를 절대 깨뜨리지 않음.

**병렬 멀티 타겟 빌드:**

```bash
stoke build --all              # stoke.toml의 모든 타겟을 병렬로
stoke build --all --force      # 위와 동일 + 캐시 무시
```

`stoke.toml`에 `project.jobs`가 설정돼 있으면 그걸로, 아니면 CPU 개수로 병렬 수 제한. 출력은 타겟별로 묶여서(`=== name [OK|FAILED] ===`) `stoke.toml`에 선언된 순서대로 출력되므로 실행할 때마다 로그가 재현 가능함. 타겟 하나가 실패해도 나머지는 계속 빌드됨 — 전체 결과 리포트를 받고, 하나라도 실패했으면 0이 아닌 종료 코드로 끝남.

### 7.5 폐쇄망/사내망 환경

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

---

## 8. 상황별 추천 세팅

**혼자 하는 프로젝트/프로토타입:** `stoke init` 하고 `lock_mode=commit` 기본값 그대로, 미러링/캐시 env var는 신경 안 써도 됨. 그냥 `stoke build && stoke run`, 반복 작업할 땐 `stoke watch`.

**작은 팀, 단일 언어:** 위와 동일 + `stoke init --language=... --yes` 한 줄을 온보딩 문서에 넣고, 언어 버전을 pin해서 팀원들 툴체인이 다 맞게 함.

**여러 언어를 쓰는 모노레포 (서비스 몇 개, 언어 다양):** 4번 섹션의 타겟 추가 흐름으로 `stoke.toml` 하나에 다 몰아넣기. CI에서 `stoke build --all`로 서비스 전체를 한 번에 빌드. Go/Rust/Kotlin/C# 서비스가 섞여 있다면, 4번 섹션에서 설명한 per-target 스코핑 수정이 들어간 stoke 버전인지 먼저 확인하고 독립 빌드를 믿을 것.

**CI 파이프라인:** 저장소에 이미 `stoke.toml`이 있으니 비대화형 init은 관련 없지만, CI에서 `stoke build --all --force`(직전 실행의 체크아웃에서 온 오래된 캐시를 못 믿으니 force) + `STOKE_REMOTE_CACHE_DIR`을 영속 캐시 볼륨으로 지정하면 CI 전용 캐시 설정 없이도 실행 간 캐싱을 얻음 — 팀 공유 캐시와 같은 메커니즘.

**폐쇄망 대기업 환경:** `STOKE_VERSION_API_BASE`/`STOKE_MAVEN_REPO_URL`(미러가 인증을 요구하면 `_USER`/`_PASSWORD` 쌍도)을 CI 환경과 팀 전체 셸 프로필/온보딩 문서에 한 번만 설정. `lock_mode=commit`과 같이 쓰면 첫 `stoke build` 이후로는 의존성 해결 때문에 인터넷에 나갈 일이 아예 없어짐.

---

## 9. stoke를 안 쓰는 게 나은 경우

- CMake, 코드 생성, 복잡한 빌드 그래프가 필요한 대규모/복잡한 C 또는 C++ 빌드 — stoke의 C/C++ 모델은 의도적으로 단순함(gcc/clang 직접 호출 + 자체 헤더 추적).
- MSVC가 꼭 필요한 Windows C++ 환경 — gcc/clang(MSYS2/MinGW 경유)만 지원됨.
- stoke 자체 소스코드를 안 건드리고 사내 전용 언어/프레임워크 템플릿을 추가하는 플러그인 시스템이 필요한 경우 — 아직 없음.
- 타겟 사이에 진짜 빌드 순서 의존성이 있는 경우(타겟 B가 빌드되려면 타겟 A의 산출물이 먼저 필요함) — `stoke build --all`은 의존성 그래프가 없고 모든 타겟을 독립적이라고 가정함.
- macOS/Linux 네이티브 설치 프로그램이 필요한 경우 — pip는 되지만 아직 설치 프로그램으로 패키징되진 않음.
- 이미 Rust/Kotlin/C#/Ruby/PHP를 대규모로 깊게 쓰고 있는 경우 — 이 다섯은 가장 최근에 추가된 언어라 원래 7개 언어만큼 대규모 실전 코드베이스에서 검증되지 않음.

---

## 10. 트러블슈팅

- **Gradle(Kotlin)이 아예 시작도 안 되고, JDK 버전을 언급하는 알쏭달쏭한 에러가 남**: 시스템 기본 JDK가 쓰고 있는 Gradle 버전에 비해 너무 새/오래됐을 수 있음(예: Gradle 8.10은 JDK 25 위에서 안 돌아감). `gradle`/`gradlew` CLI 자체를 돌리기 위해서만 `JAVA_HOME`을 지원되는 JDK로 맞춰줄 것 — 이건 `stoke.toml`의 `java_version`(프로젝트 자체가 컴파일에 쓰는 JDK를 정함)과는 별개임.
- **print 문 하나 때문에 Windows에서 `UnicodeEncodeError`로 크래시남**: Windows 콘솔의 기본 코드페이지는 로케일에 따라 다르고(예: 한글 로케일이면 `cp949`) UTF-8보다 좁음 — em-dash, 스마트 따옴표 같은 non-ASCII 문자가 콘솔 출력에 들어가면 어떤 머신에서는 크래시나고 어떤 머신에서는 안 남. stoke를 직접 확장하고 있다면 `print()` 문에는 ASCII만 쓰거나, 우회책으로 `PYTHONIOENCODING=utf-8`을 설정하거나 `chcp 65001`을 먼저 실행할 것.
- **두 번째 Go/Rust/Kotlin/C# 타겟이 독립적으로 안 빌드됨**: 4번 섹션에서 설명한 per-target 스코핑 수정이 들어가기 전 버전의 stoke를 쓰고 있을 가능성이 높음 — 업그레이드할 것.
- **공유/원격 캐시 디렉토리가 도움이 안 됨**: `STOKE_REMOTE_CACHE_DIR`이 모든 머신에서 정확히 같은 경로(또는 동등하게 매핑된 경로)로 실제 접근 가능한지, 소스 내용이 바이트 단위로 동일한지 확인할 것 — 캐시 키가 콘텐츠 해시 기반이라 공백 하나만 달라도 미스로 처리되는 게 의도된 동작임.
- **`stoke install`/`stoke build`(Java)가 사내 미러에 대고 401로 실패함**: 맞는 `_USER`/`_PASSWORD` env var 쌍(`STOKE_VERSION_API_USER`/`PASSWORD` 또는 `STOKE_MAVEN_USER`/`PASSWORD`)을 설정할 것 — 에러 메시지가 어떤 걸 설정해야 하는지 알려줌.

