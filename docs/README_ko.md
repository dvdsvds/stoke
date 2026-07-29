# stoke

여러 언어로 프로젝트를 만들고, 빌드하고, 실행하는 도구
[← 메인 README로 돌아가기](../README.md) · [English](./README_en.md)

## 소개

`stoke.toml` 하나로 가상환경, 의존성, IDE 통합, 재현 가능한 빌드를 관리
Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript 프로젝트를 같은 인터페이스로 만들고, 빌드하고, 실행
Spring Boot, FastAPI, Flask, Django, 그리고 Go/Rust/Kotlin/C#/Ruby/PHP/JavaScript/TypeScript용 웹 프레임워크 20종 스캐폴딩 지원

## 주요 기능

- **다국어 지원** — Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript 통합 관리 (12개 언어, `stoke.toml` 하나로)
- **언어 설치** — `stoke install --language=X`로 Python/JDK/gcc/Go/Node.js 자동 설치 (Rust/Kotlin/C#/Ruby/PHP는 rustup, JDK 설치 도구, dotnet 인스톨러, rbenv/rvm 등 각자의 설치 도구에 위임)
- **프레임워크 스캐폴딩** — Spring Boot, FastAPI, Flask, Django, Gin, Echo, Fiber, Chi, Actix Web, Axum, Rocket, Ktor, Spring Boot(Kotlin), ASP.NET Core, Sinatra, Slim, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono
- **Python 환경** — venv 또는 conda 선택 가능
- **자동 의존성 관리** — stoke가 직접 관리하는 언어는 pip, Maven Central, vcpkg / 나머지는 Cargo, Gradle, NuGet, Bundler, Composer, npm이 각자 처리
- **팀 일관성을 위한 버전 pin** — 이제 모든 언어에 pin 메커니즘 존재 (아래 [버전 pin](#팀-일관성을-위한-버전-pin) 참고)
- **사설 레지스트리 / 미러 지원** — 툴체인 설치와 Java의 Maven 의존성 다운로드를 사내 미러로 돌릴 수 있음, 선택적 Basic Auth 지원 (아래 [사설 레지스트리와 미러](#사설-레지스트리와-미러) 참고)
- **빌드 캐시** — content-hash 기반 캐시 무효화(mtime 기반과 달리 머신/CI 간에도 정확히 동작), C/C++·Java용 선택적 공유/원격 캐시 (아래 [빌드 캐시](#빌드-캐시) 참고)
- **병렬 멀티타겟 빌드** — `stoke build --all`로 `stoke.toml`의 모든 타겟을 동시에 빌드
- **멀티타겟 프로젝트** — 기존 프로젝트 안에서 `stoke init`을 다시 실행하면 `stoke.toml`을 직접 고치는 대신 새 타겟을 추가
- **자동 IDE 통합** — VSCode, IntelliJ, Eclipse 설정 파일 자동 생성
- **Watch 모드 + Hot-reload** — 파일 변경 감지 후 자동 재빌드, 프로세스 재시작
- **빌드 프로파일** — C/C++용 debug/release 및 커스텀 프로파일 (컴파일 플래그, defines, 컴파일러 지정)
- **재현 가능한 빌드** — lock 파일 기반 팀 재현성
- **증분 빌드** — content-hash 캐시로 안 바뀐 파일 skip
- **대화형 + 비대화형 초기화** — 사람은 `stoke init`, CI/온보딩 스크립트는 `stoke init --language=X --yes`

## 설치

### Windows (초심자 추천)
[Releases](https://github.com/dvdsvds/stoke/releases/latest)에서 인스톨러 다운로드. Python 포함되어 있어 별도 설치 필요 없음.

### pip (개발자용)
```bash
pip install stoke-build
```
pip 방식은 Python 3.11 이상 필요.

## 빠른 시작

```bash
mkdir myapp
cd myapp
stoke init
stoke build
stoke run
```

## 지원 언어

| 언어 | stoke가 위임하는 빌드 도구 | 버전 pin |
| --- | --- | --- |
| Python | pip / venv / conda (자체 의존성 해석 + lock) | `stoke.toml`의 `python_version`, 감지된 설치와 대조해 강제 |
| Java | `javac` 직접 호출 (의존성은 Maven Central, 빌드는 Maven 안 씀) | `stoke.toml`의 `java_version`, 감지된 JDK와 대조해 강제 |
| C | gcc/clang 직접 호출, 자체 헤더 의존성 추적 | `stoke.toml`의 `c_standard` |
| C++ | gcc/clang 직접 호출, 자체 헤더 의존성 추적 | `stoke.toml`의 `cpp_standard` |
| Go | `go build` / `go run` | 선택적 pin, `go.mod`의 `go`/`toolchain` 지시문 (Go 툴체인 자체가 읽음) |
| Rust | `cargo build --release` / run | 선택적 `rust-toolchain.toml` (rustup이 읽음) |
| Kotlin | Gradle Wrapper(`gradlew`) 또는 시스템 `gradle` | `stoke.toml`의 `java_version`, `-Dorg.gradle.java.home`으로 강제 |
| C# | `dotnet build` / `dotnet run` | 선택적 `global.json` (dotnet CLI가 읽음) |
| Ruby | Bundler + `ruby` (Gemfile 있으면 `bundle exec ruby`) | 선택적 `.ruby-version` (rbenv/rvm/asdf/chruby가 읽음) |
| PHP | Composer + `php` | 선택적 `composer.json`의 `require.php` 제약 (`composer install`이 강제) |
| JavaScript | Node.js (`npm install` + `node <entry>`) | 선택적 pin, `.nvmrc` + `package.json`의 `engines.node` |
| TypeScript | Node.js + tsx (컴파일+실행 한 번에) | 선택적 pin, `.nvmrc` + `package.json`의 `engines.node` |

C/C++ 의존성 관리는 vcpkg 사용. Python/Java는 stoke 자체 lock 파일(`stoke.lock`) 사용. 나머지 언어는 각 생태계 자체 lock 파일에 전적으로 위임 (`Cargo.lock`, `package-lock.json`, `Gemfile.lock`, `composer.lock`, `go.sum`, Gradle 자체 해석).

## 명령어

### 프로젝트 관리

| 명령어 | 설명 |
| --- | --- |
| `stoke init` | 대화형 프로젝트 초기화. 기존 프로젝트 안에서 다시 실행하면 덮어쓰는 대신 새 타겟 추가 |
| `stoke init <framework>` | 프레임워크 프로젝트 바로 생성 ([프레임워크 스캐폴딩](#프레임워크-스캐폴딩) 참고) |
| `stoke init --language=<lang> [--version] [--name] [--env-type] [--lock-mode] [--vcpkg] [--yes]` | 프롬프트 없는 비대화형 초기화 (CI/온보딩 스크립트용) |
| `stoke build [target]` | 타겟 빌드 (생략하면 `stoke.toml`의 첫 번째 타겟) |
| `stoke build --all` | `stoke.toml`의 모든 타겟을 병렬로 빌드 |
| `stoke build --force` | 캐시 무시하고 전체 재빌드 |
| `stoke build --debug` / `--release` / `--profile=<name>` | 특정 프로파일로 빌드 (C/C++) |
| `stoke run [target]` | 빌드된 타겟 실행 |
| `stoke watch [target]` | 파일 변경 감지 후 자동 재빌드 |
| `stoke hot-reload [target]` | 재빌드 + 실행 중인 프로세스 재시작 |
| `stoke clean [target]` | 빌드 산출물 삭제 |
| `stoke clean --all` | lock 파일 포함 완전 초기화 |
| `stoke ide-sync` | VSCode/Eclipse/IntelliJ 설정 파일 재생성, 워크스페이스 IDE 파일도 관리 |

### 언어별 도구

| 명령어 | 설명 |
| --- | --- |
| `stoke python list` | 설치된 파이썬 목록 |
| `stoke java list` | 설치된 JDK 목록 |
| `stoke c list` | 설치된 C 컴파일러 (gcc) |
| `stoke cpp list` | 설치된 C++ 컴파일러 (g++) |

Rust/Kotlin/C#/Ruby/PHP 툴체인은 `PATH`에 있는 걸 그대로 감지합니다 — 이들을 위한 `stoke <lang> list`는 없습니다. Kotlin은 Java의 JDK 감지 로직을 그대로 재사용합니다.

### 도구 관리

| 명령어 | 설명 |
| --- | --- |
| `stoke install vcpkg` | vcpkg 설치 (`~/.stoke/tools/vcpkg/`) |
| `stoke uninstall vcpkg` | vcpkg 제거 |
| `stoke install --language=<lang> --version=<ver> [--base-url=<url>]` | 언어 툴체인 설치 (`python`, `java`, `c`, `cpp`, `go`, `nodejs`; 기본 버전: `latest`) |
| `stoke install --language=<lang> --list [--base-url=<url>]` | 해당 언어의 설치 가능한 버전 목록 조회 |
| `stoke uninstall --language=<lang> [--version=<ver>]` | 설치된 툴체인 제거 |

`--base-url`(또는 `STOKE_VERSION_API_BASE` 환경변수)을 쓰면 stoke 기본 엔드포인트 대신 사내 미러를 가리킬 수 있습니다 — [사설 레지스트리와 미러](#사설-레지스트리와-미러) 참고.

### 프레임워크 스캐폴딩

`stoke init <framework>`로 즉시 실행 가능한 프레임워크 프로젝트를 생성합니다:

| 언어 | 프레임워크 |
| --- | --- |
| Python | `fastapi`, `flask`, `django` |
| Java | `spring-boot` |
| Go | `gin`, `echo`, `fiber`, `chi` |
| Rust | `actix-web`, `axum`, `rocket` |
| Kotlin | `ktor`, `spring-boot-kotlin` |
| C# | `aspnet-core` |
| Ruby | `sinatra` |
| PHP | `slim` |
| JavaScript | `express`, `fastify` |
| TypeScript | `nextjs`, `nestjs`, `vite`, `nuxt`, `sveltekit`, `hono` |

Rails와 Laravel은 의도적으로 제외했습니다 — 둘 다 엔트리 스크립트를 직접 실행하는 게 아니라 CLI 서브커맨드(`bin/rails server`, `php artisan serve`)로 시작하는 구조라 stoke의 실행 모델과 안 맞습니다. 대신 그 모델에 맞는 Sinatra/Slim을 선택했습니다.

### C/C++ 라이브러리 관리 (vcpkg)

| 명령어 | 설명 |
| --- | --- |
| `stoke vcpkg install <library>` | 라이브러리 설치 (최신 버전) |
| `stoke vcpkg install <library> --version=X` | 특정 버전 설치 |
| `stoke vcpkg remove <library>` | 라이브러리 제거 |
| `stoke vcpkg list` | 설치된 라이브러리 목록 |
| `stoke vcpkg version` | vcpkg 버전 확인 |

## 언어별 설정 예시

### Python

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "python"
python_version = "3.12"
sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.myapp.deps]
requests = "2.31.0"
fastapi = ">=0.100.0"
```

### Java

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "java"
java_version = "21"
sources = ["src/**/*.java"]
main_class = "com.example.Main"

[targets.myapp.deps]
"com.google.code.gson:gson" = "2.10.1"
```

### C

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "c"
c_standard = "c17"
sources = ["src/**/*.c"]
```

### C++

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "cpp"
cpp_standard = "c++17"
sources = ["src/**/*.cpp"]

[targets.myapp.deps]
fmt = "latest"
```

### Go

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "go"
```

의존성은 `stoke.toml`이 아니라 `go.mod`로 관리합니다. `stoke init`에서 선택적으로 `go_version`을 `go.mod`의 `go`/`toolchain` 지시문에 pin할 수 있습니다.

### Rust

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "rust"
```

의존성은 `Cargo.toml`로 관리합니다. `stoke init`에서 선택적으로 `rust-toolchain.toml`을 써서 툴체인 버전을 pin할 수 있습니다 (rustup이 자동으로 읽음).

### Kotlin

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "kotlin"
java_version = "21"
```

의존성은 `build.gradle.kts`로 관리합니다. `java_version`은 실제로 강제됩니다 — stoke가 일치하는 JDK를 찾아서 `-Dorg.gradle.java.home`으로 Gradle에 넘깁니다.

### C#

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "csharp"
```

의존성(NuGet)은 `.csproj`로 관리합니다. `stoke init`에서 선택적으로 `global.json`을 써서 .NET SDK 버전을 pin할 수 있습니다 (dotnet CLI가 자동으로 읽음).

### Ruby

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "ruby"
entry = "src/main.rb"
```

의존성은 Bundler의 `Gemfile`로 관리합니다 (`Gemfile`이 있으면 자동으로 `bundle exec ruby` 사용). `stoke init`에서 선택적으로 `.ruby-version`을 쓸 수 있습니다 (rbenv/rvm/asdf/chruby가 읽음).

### PHP

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "php"
entry = "src/main.php"
```

의존성은 Composer의 `composer.json`으로 관리합니다. `stoke init`에서 선택적으로 `composer.json`에 `require.php` 버전 제약을 넣을 수 있습니다 (`composer install` 자체가 강제).

### JavaScript

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "javascript"
entry = "src/main.js"
```

의존성은 `package.json`으로 관리합니다 (`stoke build` 실행 시 `npm install` 수행). `stoke init`에서 선택적으로 Node 버전을 `.nvmrc`와 `package.json`의 `engines.node`에 pin할 수 있습니다.

### TypeScript

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "typescript"
entry = "src/main.ts"
```

`tsx`로 실행됩니다. 의존성은 `package.json`으로 관리하며, Node 버전 pin은 위 JavaScript와 동일합니다.

## 팀 일관성을 위한 버전 pin

- **Python/Java**: `stoke.toml`의 `python_version`/`java_version`, 빌드 시 설치된 툴체인과 대조.
- **C/C++**: `stoke.toml`의 `c_standard`/`cpp_standard`.
- **Kotlin**: `stoke.toml`의 `java_version` — stoke가 일치하는 JDK를 찾아서 `-Dorg.gradle.java.home`으로 Gradle에 넘김, 일치하는 게 없으면 명확히 실패.
- **Rust**: 선택적 `rust-toolchain.toml` — rustup이 자동으로 읽음.
- **C#**: 선택적 `global.json` — dotnet CLI가 자동으로 읽음.
- **Ruby**: 선택적 `.ruby-version` — rbenv/rvm/asdf/chruby가 자동으로 읽음.
- **PHP**: 선택적 `composer.json`의 `require.php` 제약 — `composer install`이 강제.
- **Go**: 선택적 pin, `go.mod`의 `go` 지시문(최소 버전, `go build` 자체가 강제)과 `toolchain` 지시문(정확한 버전 — `GOTOOLCHAIN=auto`가 기본값인 Go 1.21+에서는 Go 툴체인 매니저가 알아서 해당 버전을 자동 다운로드)에 patch.
- **JavaScript/TypeScript**: 선택적 `node_version` pin, `.nvmrc`(nvm/fnm이 읽음)와 `package.json`의 `engines.node`에 씀. Ruby의 `.ruby-version`과 같은 급의 소프트 pin — `npm install`이 버전 안 맞으면 경고만 하고 기본적으로 막지는 않음 (`.npmrc`의 `engine-strict=true`는 일부러 같이 안 씀 — 의존성 트리 안 다른 패키지의 `engines`까지 엄격 검사 대상이 될 수 있어서).

선택적 pin(Rust, C#, Ruby, PHP, Go, JavaScript, TypeScript)은 전부 `stoke init` 진행 중에 프롬프트로 물어봅니다 — 빈 입력이면 pin을 건너뜁니다. stoke가 직접 버전을 강제하는 게 아니라, 각 언어 생태계의 툴체인 매니저가 이미 읽을 줄 아는 네이티브 파일을 하나 써두는 방식입니다.

## 사설 레지스트리와 미러

특정 내부 호스트만 화이트리스트로 열어둔 네트워크를 위해, 툴체인 설치와 Java 의존성 다운로드를 사내 미러로 돌릴 수 있습니다:

```bash
# stoke install --language=X --version=Y (툴체인 다운로드 + 버전 목록 조회)
stoke install --language=python --version=3.12 --base-url=https://internal-mirror.company.com/stoke-versions
# 또는 조직/CI 전체에 한 번만 설정:
export STOKE_VERSION_API_BASE=https://internal-mirror.company.com/stoke-versions

# stoke build (Java의 Maven 의존성 다운로드)
export STOKE_MAVEN_REPO_URL=https://internal-mirror.company.com/maven2
stoke build
```

둘 다 Sonatype Nexus 기준으로 검증됨 (버전 JSON용 `raw` hosted repository, Java 의존성용 Nexus 내장 `maven-central` 프록시).

**인증이 필요한 미러**도 둘 다 지원합니다, HTTP Basic Auth로 (자격증명은 헤더로만 전달, URL에는 절대 안 들어감):

```bash
export STOKE_MAVEN_USER=ci-user
export STOKE_MAVEN_PASSWORD=***          # stoke build (Java)용
export STOKE_VERSION_API_USER=ci-user
export STOKE_VERSION_API_PASSWORD=***    # stoke install용
```

설정 안 하면 `Authorization` 헤더 자체를 안 보냄 — 익명 미러는 기존과 동일하게 동작합니다.

여기서 다루는 건 `stoke install`(툴체인 다운로드)과 Java 프로젝트 의존성 다운로드뿐입니다. 다른 모든 언어의 프로젝트 의존성은 이미 각자 생태계의 네이티브 미러/레지스트리 설정을 투명하게 따릅니다 (pip.conf, `.npmrc`, NuGet.config, `.cargo/config.toml`, Bundler/Composer 설정, vcpkg 레지스트리) — stoke 쪽에서 따로 할 일 없습니다.

## 빌드 캐시

- **Content-hash 무효화 (캐시를 쓰는 모든 언어)** — `.stoke/cache.json`이 mtime/size 대신 파일의 SHA-256 content hash로 무효화 여부를 판단해서, 다른 머신에서 새로 체크아웃해도(내용은 같은데 mtime만 다름) 캐시를 정상적으로 재사용함.
- **원격/공유 캐시 (C/C++, Java)** — 여러 머신에서 접근 가능한 디렉토리(네트워크 공유, NAS, 매핑된 드라이브)를 `STOKE_REMOTE_CACHE_DIR`로 지정하면, 별도 캐시 서버 프로토콜 없이 `stoke build`가 컴파일된 오브젝트를 그 디렉토리에서 가져오거나 올림. C/C++은 컴파일된 `.o` 파일 단위(hit마다 헤더 content 매니페스트로 재검증), Java는 타겟 전체 단위(`javac`가 한 번의 호출로 배치 컴파일하기 때문에 파일 1:1 매핑이 없음)로 캐싱. 캐시 디렉토리가 없거나 접근 불가능하거나 오류가 나도 fail open — 빌드를 절대 깨뜨리지 않고 속도 향상만 못 받음.
- **범위** — C/C++, Java 컴파일만 해당. Python은 캐싱할 만한 컴파일 단계가 없음. Rust/Kotlin/C#/Ruby/PHP/Go/JS/TS는 각자 자기 빌드 도구(Cargo, Gradle, dotnet 등)에 위임하는 구조라, stoke 캐시 모듈과는 완전히 별개의 캐싱 스토리를 가짐.

## Lock 파일 모드

- **`commit`** — 프로젝트 루트에 `stoke.lock`, git 커밋 대상 (팀 재현성)
- **`local`** — `.stoke/lock.toml`, gitignore 대상 (개발자별 관리)

## 의존성 버전 문법

`stoke.toml`에 `[targets.<name>.deps]` 테이블이 있는 언어는 Python, Java, C/C++뿐입니다 — 나머지 언어는 전부 각자의 네이티브 매니페스트(`Cargo.toml`, `build.gradle.kts`, `.csproj`/NuGet, `Gemfile`, `composer.json`, `package.json`)로 의존성을 관리하므로, 위 설정 예시 이상으로 stoke 쪽에서 설정할 게 없습니다.

### Python (pip specifier)

- `"2.31.0"` — 정확한 버전
- `">=2.0.0"`, `"<3.0.0"` — 버전 범위
- `"*"` 또는 `""` — 아무 버전

### Java (Maven 좌표)

- `"groupId:artifactId" = "version"`
- 예시: `"com.google.code.gson:gson" = "2.10.1"`

### C/C++ (vcpkg)

- `"latest"` — 최신 버전 (기본값)
- `"10.2.1"` — 특정 버전

## IDE 통합

### Python

- `.vscode/settings.json` — 파이썬 인터프리터 경로

### Java

- `.classpath`, `.project` — Eclipse, VSCode Java 확장
- `pom.xml` — IntelliJ IDEA, Maven 기반 IDE
- `.vscode/settings.json` — 참조 라이브러리

### C / C++

- `compile_commands.json` — clangd, VSCode C/C++ 확장, CLion
- `.vscode/c_cpp_properties.json` — VSCode C/C++ 확장

### Go / Rust / Kotlin / C# / Ruby / PHP / JavaScript / TypeScript

stoke가 관리하는 IDE 파일은 아직 없습니다 — 각 언어의 에디터 툴링을 그대로 사용합니다 (`gopls`, `rust-analyzer`, Kotlin/IntelliJ 플러그인, OmniSharp/C# 확장, Solargraph, Intelephense, 내장 TS/JS 언어 서비스).

### 워크스페이스 (여러 프로젝트)

`stoke ide-sync` 실행 시 워크스페이스 루트에 `<폴더이름>.code-workspace` 생성

VSCode에서 `File > Open Workspace from File`로 열면 각 프로젝트가 독립된 root로 인식

## 동작 방식

`stoke build` 실행 시:

1. `stoke.toml` 파싱 후 타겟 결정 (`--all`이면 모든 타겟을 병렬로)
2. 언어별 처리:
   - Python: venv 생성 → pip 의존성 설치 → 문법 체크
   - Java: JDK 감지 → Maven 의존성 다운로드(미러 경유 가능) → `javac` 컴파일, 빌드 캐시 활용
   - C/C++: 컴파일러 감지 → vcpkg 의존성 설치 → `gcc`/`g++` 컴파일 + 링크, 빌드 캐시 활용
   - Go: `go` 툴체인 감지 (`go.mod`의 버전 pin 존중) → `go build`
   - Rust: `cargo build --release`, `rust-toolchain.toml`이 있으면 그걸 따름
   - Kotlin: 일치하는 JDK 결정 (`java_version`) → `gradlew`/`gradle` 빌드, 올바른 (서브)프로젝트로 범위 제한
   - C#: `dotnet build`, `global.json`이 있으면 그걸 따름, 올바른 `.csproj` 대상으로
   - Ruby: `Gemfile`이 있으면 `bundle exec ruby`, 없으면 `ruby` 직접 실행
   - PHP: `composer.json`이 있으면 `composer install`(PHP 버전 제약도 같이 강제), 그 다음 `php` 실행
   - JavaScript/TypeScript: Node.js 감지 (`.nvmrc`/`engines.node` pin 존중) → `npm install` (`package.json`이 있을 때) → `node`/`tsx`로 실행
3. IDE 통합 파일 생성 (`.classpath`, `pom.xml`, `compile_commands.json` 등, Python/Java/C/C++ 대상)
4. `.gitignore` 자동 관리
5. lock 파일 저장 (변경 시에만)
6. 캐시 저장 (`.stoke/cache.json`, `STOKE_REMOTE_CACHE_DIR`가 설정돼 있으면 원격 캐시 디렉토리에도)

## Python 프로젝트 설정

### Entry 파일 지정

`stoke.toml`의 `entry` 필드는 실행할 파이썬 파일의 경로입니다. 기본값은 `src/main.py`입니다.

파일 이름이나 위치를 바꾸려면 `stoke.toml`을 직접 수정하세요:

```toml
[targets.myapp]
entry = "src/myapp/main.py"        # 커스텀 위치
# entry = "src/computer_main.py"   # 커스텀 이름
```

### 프로젝트 구조 관행

파이썬은 하위 폴더의 모듈을 사용하려면 명시적인 경로가 필요합니다.

**폴더 구조**:
src/
├── main.py
└── computer/
├── init.py
└── hardware/
├── init.py
└── cpu.py

**main.py의 import**:
```python
from computer.hardware.cpu import CPU
```

**주의**:
- 각 하위 폴더에 `__init__.py`가 있어야 함 (빈 파일도 됨)
- 짧은 이름 (`from cpu import CPU`)은 안 됩니다. 폴더 경로가 필요합니다.

## 알려진 한계

- macOS/Linux 네이티브 설치파일 아직 없음 (pip는 되지만 end-to-end 검증은 안 됨)
- C/C++용 CMake/Meson 통합 없음 — stoke는 자체 단순 빌드 모델이라 대형/생성형 C/C++ 빌드 그래프는 안 맞음
- C/C++용 MSVC(`cl.exe`) 미지원, gcc/clang만
- pre/post-build 훅 시스템 없음
- 플러그인/확장 시스템 없음 — 사내 전용 언어/프레임워크 템플릿을 추가하려면 아직 stoke 소스 자체를 고쳐야 함
- Rust, Kotlin, C#, Ruby, PHP는 가장 최근에 추가된 언어라, 커맨드 생성/템플릿은 검증됐지만 각 생태계의 대형 실전 프로젝트로는 아직 충분히 검증 안 됨
- 타겟 간 의존성 그래프 없음 — `stoke build --all`은 모든 타겟을 독립적이라고 가정
- Rails, Laravel 스캐폴딩은 의도적으로 제외 ([프레임워크 스캐폴딩](#프레임워크-스캐폴딩) 참고)

전체 현황(검증된 것/남은 gap/대규모 조직에 맞는지 여부)은 저장소 루트의 [`FEATURES.ko.md`](../FEATURES.ko.md)를 참고하세요.

## 로드맵
- **v0.1** — Python 빌드 (venv, 의존성, 문법 체크, 증분 빌드)
- **v0.2** — Watch 모드, hot-reload
- **v0.3** — Java 지원 (JDK 감지, Maven Central, IDE 통합)
- **v0.4** — C/C++ 지원 (gcc/g++, watch, hot-reload, IDE 통합)
- **v0.5** — vcpkg 통합, 도구 관리, multi-root workspace
- **v0.6** — C/C++ 빌드 개선 (헤더 의존성 자동 추적, 병렬 컴파일, IDE 통합 자동화)
- **v0.7** — 빌드 프로파일 시스템 (debug/release, 커스텀 프로파일, clang 지원)
- **v0.8** — CLI help 한국어 지원 (STOKE_LANG 환경변수), 내부 리팩토링
- **v1.0** — 언어 설치 기능
  - CLI: `stoke install --language=X --version=Y`
  - 자체 버전 API (GitHub Pages)
  - Python, Java, C/C++ 지원
- **v1.1** — Go 언어 지원 (설치, 빌드, 실행, 제거), Go 프레임워크 스캐폴딩 (Gin, Echo, Fiber, Chi)
- **v1.2** — Node.js 설치 지원
- **v1.3** — JavaScript, TypeScript 지원, 웹 프레임워크 8종 추가 (Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono)
- **v1.4** — Rust, Kotlin, C#, Ruby, PHP 지원 (총 12개 언어, 24개 프레임워크); CI/온보딩용 비대화형 `stoke init --language=X`; 새 5개 언어 버전 pin + Kotlin `java_version` 실제 강제; 툴체인 설치와 Java Maven 의존성용 사설 레지스트리/미러 지원(인증 포함); content-hash 빌드 캐시 무효화 + C/C++·Java용 원격/공유 캐시(`STOKE_REMOTE_CACHE_DIR`); 병렬 멀티타겟 빌드(`stoke build --all`); `stoke init`으로 기존 프로젝트에 타겟 추가; Go/Rust/Kotlin/C# 어댑터가 항상 프로젝트 루트 전체를 재빌드하던 문제 수정 — 이제 타겟별로 독립 빌드
- **v1.5** — Go(`go.mod`의 `go`/`toolchain` 지시문), JavaScript/TypeScript(`.nvmrc` + `package.json`의 `engines.node`) 버전 pin 추가

## 라이선스

MIT
