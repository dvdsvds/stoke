# stoke init

대화형으로 새 stoke 프로젝트를 생성합니다.

## 사용법

```bash
stoke init
```

현재 디렉토리에서 대화형 마법사를 실행합니다.

```bash
stoke init <framework>
```

마법사를 건너뛰고 특정 프레임워크를 바로 스캐폴딩합니다 (예: `stoke init fastapi`, `stoke init gin`). 전체 목록은 [프레임워크 스캐폴딩](../frameworks/overview.md)을 참고하세요.

## 동작 방식

마법사가 다음을 물어봅니다:

1. **프로젝트 이름** — 기본값은 현재 폴더 이름
2. **언어** — Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript
3. **언어 버전** — Python 3.12, Java 25, C11, C++20 등 (Go/JavaScript/TypeScript는 버전을 아예 안 물어보고 PATH에 있는 툴체인을 그대로 씀; Kotlin은 Java 감지 로직을 재사용해서 JDK 버전을 물어봄; Rust/C#/Ruby/PHP는 *선택적인* 툴체인 버전 고정을 물어봄 — 자세한 내용은 [비대화형 모드](#non-interactive-mode-ci-team-onboarding)와 각 언어 페이지 참고)
4. **진입점 / 메인 클래스** — 언어에 따라 다름
5. **의존성** — 선택사항

그 다음 생성되는 것:

- `stoke.toml` — 프로젝트 설정
- `src/` — 소스 디렉토리
- hello-world 소스 파일

## 예시: C++ 프로젝트
$ mkdir myapp && cd myapp
$ stoke init
Project name [myapp]:
Language [python/java/c/cpp]: cpp
C++ standard [17/20/23] [20]:
Executable name [myapp]:
Install vcpkg for C/C++ library management? [y/N]: n
Created:
stoke.toml
src/main.cpp
Try:
stoke build
stoke run

생성된 `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]
cpp_standard = "c++20"
```

## 예시: Python 프로젝트
$ mkdir myapp && cd myapp
$ stoke init
Project name [myapp]:
Language [python/java/c/cpp]: python
Python version [3.10/3.11/3.12/3.13]: 3.12
Entry file [src/main.py]:
Created:
stoke.toml
src/main.py

생성된 `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "python"
python_version = "3.12"
entry = "src/main.py"
sources = ["src/**/*.py"]
```

## 예시: Java 프로젝트
$ mkdir myapp && cd myapp
$ stoke init
Project name [myapp]:
Language [python/java/c/cpp]: java
Java version [17/21/25]: 25
Package [com.myapp]:
Main class [Main]:
Created:
stoke.toml
src/main/java/com/myapp/Main.java

생성된 `stoke.toml`:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "java"
java_version = "25"
sources = ["src/main/java/**/*.java"]
main_class = "com.myapp.Main"
```

## 비대화형 모드 (CI / 팀 온보딩) { #non-interactive-mode-ci-team-onboarding }

프롬프트를 쓸 수 없는 스크립트, CI, 스캐폴딩 도구에서는 `--language`를 넘기면 stoke가 마법사를 완전히 건너뜁니다:

```bash
stoke init --language=rust --name=myapp --version=1.75.0 --lock-mode=commit --yes
```

| 플래그 | 의미 |
| --- | --- |
| `--language` | 필수. `python`, `java`, `c`, `cpp`, `go`, `rust`, `kotlin`, `csharp`, `ruby`, `php`, `javascript`, `typescript` 중 하나 |
| `--name` | 프로젝트 이름. 기본값은 현재 폴더 이름 |
| `--version` | 언어에 따라 의미가 다름 (아래 표 참고). 생략하면 적절한 기본값 사용 |
| `--env-type` | `venv` 또는 `conda`. Python 전용, 기본값은 `venv` |
| `--lock-mode` | `commit` 또는 `local`. 기본값은 `commit` |
| `--vcpkg` | vcpkg가 없으면 설치. C/C++ 전용 |
| `--yes` | 기존 `stoke.toml`을 묻지 않고 덮어씀. 이 플래그가 없으면 `stoke.toml`이 이미 있을 때 init이 명확히 실패함 — 스크립트에서 팀원 설정을 조용히 덮어쓰는 것보다 안전함 |

언어별 `--version` 의미:

| 언어 | `--version`의 의미 | 생략 시 기본값 |
| --- | --- | --- |
| Python | Python 버전 (예: `3.12`) | 시스템에서 감지된 기본 설치 |
| Java | JDK 버전 (예: `21`) | 시스템에서 감지된 기본 설치 |
| Kotlin | JDK 버전, `stoke.toml`에는 `java_version`으로 기록됨 | 시스템에서 감지된 기본 설치 |
| C | C 표준 (예: `c17`) | `c17` |
| C++ | C++ 표준 (예: `c++20`) | `c++17` |
| Rust | 선택적 툴체인 고정, `rust-toolchain.toml`에 기록됨 | 기록 안 함 (고정 없음) |
| C# | 선택적 SDK 고정, `global.json`에 기록됨 | 기록 안 함 (고정 없음) |
| Ruby | 선택적 버전 고정, `.ruby-version`에 기록됨 | 기록 안 함 (고정 없음) |
| PHP | 선택적 버전 제약, `composer.json`의 `require.php`에 기록됨 | 기록 안 함 (고정 없음) |
| Go, JavaScript, TypeScript | 사용 안 함 | — |

종료 코드가 의미 있게 반환되므로(`0` 성공, 0 아니면 실패) 온보딩 스크립트에 깔끔하게 조합할 수 있습니다:

```bash
#!/usr/bin/env bash
set -e
mkdir myapp && cd myapp
stoke init --language=python --version=3.12 --lock-mode=commit --yes
stoke build
```

## 팀 일관성을 위한 버전 고정

Rust, C#, Ruby, PHP는 stoke 안에 Python/Java처럼 자체 버전 매니저 개념이 없어서, `stoke init`은 대신 각 생태계의 표준 고정 파일을 선택적으로 써줄 수 있습니다 — git에 커밋해두면 모든 팀원의 `stoke build`가 같은 툴체인 버전을 쓰게 하거나(안 맞으면 명확히 실패):

- **Rust** → `rust-toolchain.toml` (`rustup`이 자동으로 읽음)
- **C#** → `global.json` (`dotnet` CLI가 자동으로 읽음)
- **Ruby** → `.ruby-version` (rbenv/rvm/asdf/chruby가 자동으로 읽음)
- **PHP** → `composer.json`의 `require.php` 제약 (`composer.json`이 존재하면 `stoke build`의 일부로 실행되는 `composer install`이 강제함)
- **Kotlin** → `stoke.toml`의 기존 `java_version` 필드를 stoke 자신이 강제함: `stoke build`/`stoke run`이 맞는 JDK를 찾아서 `-Dorg.gradle.java.home`으로 Gradle에 전달하고, 맞는 JDK가 없으면 명확한 에러로 실패

대화형 마법사에서는 이 질문들이 선택사항이고(비워두면 건너뜀), 비대화형 모드에서는 `--version`을 넘겼을 때만 적용됩니다.

## init 이후

빌드하고 실행:

```bash
stoke build
stoke run
```

## 관련 문서

- [빠른 시작](../getting-started/quick-start.md)
- [`stoke.toml` 레퍼런스](../configuration/stoke-toml.md)
