# 언어/프레임워크 버전 하드코딩 현황과 해결 방향

- 날짜: 2026-09-17
- 종류: design
- 상태: Kotlin 컴파일러 버전 부분만 부분 수정 (아래 "수정" 참고), 라이브 조회 자체는 미구현

## 결론부터

`stoke install <language>`가 실제로 받아오는 툴체인 버전(`src/stoke/install_versions.py` + `src/stoke/cli/install_lang.py`)은 **문제 없음** — `https://dvdsvds.github.io/stoke/versions/<lang>.json`을 라이브로 fetch하고, 실패하면 하드코딩된 대체 목록 없이 그냥 에러를 냄. 즉 "몰래 오래된 버전 목록을 쓰는" 위험은 여기 없음. staleness 위험은 딱 한 곳에 몰려있음: **Kotlin 프레임워크 스캐폴딩이 생성하는 `build.gradle.kts`에 박히는 버전 숫자들**.

## 실제로 하드코딩되어 있고 문제인 것

| 위치 | 값 | 비고 |
|---|---|---|
| `kotlin/init.py:82` | `kotlin("jvm") version "1.9.24"` | 라이브 조회 없음, 유일한 소스 |
| `kotlin/frameworks/ktor.py:65` | `kotlin("jvm") version "1.9.24"` | init.py와 동일 값 중복 |
| `kotlin/frameworks/ktor.py:74-75` | `ktor-server-core-jvm:2.3.12`, `ktor-server-netty-jvm:2.3.12` | Ktor 3.x가 나온 지 오래됐는데 2.3대 고정 |
| `kotlin/frameworks/spring_boot.py:66-69` | `org.springframework.boot:3.3.4`, `io.spring.dependency-management:1.1.6`, `kotlin("jvm"):1.9.24`, `kotlin("plugin.spring"):1.9.24` | 전부 고정, 전부 중복 |

**흥미로운 점**: 같은 `kotlin/init.py` 파일 안에서 Gradle 버전은 `https://services.gradle.org/versions/current`로 라이브 조회하면서(11-25번째 줄, 실패 시 시스템 gradle로 폴백) Kotlin 컴파일러 플러그인 버전은 왜 하드코딩인지 기술적 이유가 없음 — 그냥 그 부분만 안 고친 것으로 보임. 같은 리터럴이 3개 파일에 복붙되어 있어서 고치려면 3곳을 다 고쳐야 함(중앙화 안 됨).

## 낮은 위험으로 판단한 것들 (참고용, 조치 불필요)

- **C#**: `csharp/init.py:75`의 `net8.0`은 `dotnet` CLI가 아예 없을 때만 쓰는 폴백 (있으면 `dotnet new console`이 알아서 현재 SDK 기준으로 생성). `_select_csharp_version()`은 기본이 "핀 안 함"이라 정상 패턴.
- **Rust**: `rust/init.py:66`의 `edition = "2021"`도 `cargo` 없을 때만 쓰는 폴백. rustc 버전 자체는 핀 안 함(기본 blank)이 정상 패턴.
- **Java**: `java/init.py:12`의 `"21"`은 로컬에 JDK가 하나도 없을 때 프롬프트 기본값일 뿐 — 사용자가 얼마든지 다른 값 입력 가능, 설치 타겟도 아님.
- **Python/Go/Ruby/PHP/C/C++/JS/TS**: 하드코딩된 언어 버전 없음. Python/Node는 로컬 설치본 중 선택하거나 명시적 핀(기본 blank)이라 정상.
- `python/versions.py`의 `range(8, 15)`(3.8~3.14 스캔) 같은 "로컬에 설치된 버전을 찾을 때 훑는 범위"는 버전을 설치하는 게 아니라 감지하는 거라 최신 버전이 나오면 스캔 범위만 넓혀주면 됨 — 연 1회 정도 유지보수 필요하지만 지금 당장 문제는 아님(Python 3.14가 2025년 10월 나왔고 범위가 3.14까지 커버함).

## 패턴 일관성 진단

이 코드베이스에 버전을 정하는 방식이 3가지 섞여 있음:

1. **라이브 조회, 하드코딩 폴백 없음** — `install_versions.py`를 통한 `stoke install <lang>` (python/java/c/cpp/go/nodejs/rust/csharp/ruby/php 전부). 좋음. 단, 이건 "stoke가 설치해주는 버전"이지 "스캐폴딩된 프로젝트 설정 파일에 박히는 버전"과는 다른 축.
2. **사용자 핀, 기본값은 안 핀(blank)** — Rust rustc, C# SDK, Node, Python 버전 선택. 좋음, 로컬에 이미 설치된 걸 그대로 씀.
3. **하드코딩 리터럴, 라이브 조회도 폴백 프레이밍도 없음** — Kotlin 컴파일러 플러그인 버전, Ktor/Spring Boot(Kotlin) 플러그인 버전들. 딱 여기만 실제로 "조용히 낡아가는 하드코딩 배열" 패턴이고, 같은 파일의 형제 코드(Gradle 버전)와도 일관성이 없음.

## 제안하는 해결 방향

전면적인 시스템 개편은 불필요 — 이미 검증된 패턴(`kotlin/init.py`의 Gradle 라이브 조회 + 실패 시 폴백)을 Kotlin 컴파일러 플러그인 버전에도 그대로 적용하면 됨. 구체적으로:

1. Kotlin 버전을 Maven Central 또는 Kotlin 릴리스 API에서 라이브 조회하는 헬퍼를 하나 만들고(`_current_gradle_version()`과 같은 자리에), 실패 시에만 상수로 폴백.
2. `"1.9.24"` 리터럴이 3개 파일에 중복되어 있는 걸 한 곳(예: `kotlin/init.py`에 `_DEFAULT_KOTLIN_VERSION` 같은 이름으로)에 정의하고 `ktor.py`/`spring_boot.py`가 그걸 import해서 쓰도록 정리.
3. Ktor(`2.3.12`)와 Spring Boot(`3.3.4`)도 같은 패턴 확장 후보지만, 우선순위는 Kotlin 컴파일러 버전보다 낮음(둘 다 2단계 메이저 차이까지는 아니고, 새 프로젝트가 당장 안 돌아가는 수준은 아님).

C#/Rust의 폴백 값(`net8.0`, `edition = "2021"`)은 어차피 거의 안 타는 경로(CLI 도구가 없을 때만)라 건드릴 거면 김에 최신값으로 한 줄만 바꾸는 정도로 충분, 급하지 않음.

## 실제로 한 조치 (라이브 조회 대신 중앙화 + 갱신을 택함)

Kotlin 컴파일러 릴리스 API로 라이브 조회하는 헬퍼는 만들지 않음 — Gradle처럼 공식 API가 명확히 있는 게 아니라서 범위가 커짐. 대신 우선순위가 더 높았던 "3개 파일에 중복된 하드코딩" 문제를 해결:

- `kotlin/init.py`에 `DEFAULT_KOTLIN_VERSION = "2.1.0"` 상수를 정의(1.9.24 → 2.1.0으로 갱신)하고, `ktor.py`/`spring_boot.py`(Kotlin)가 이걸 import해서 쓰도록 변경. 이제 버전을 올리려면 한 곳만 고치면 됨.
- Kotlin Spring Boot의 `org.springframework.boot` 버전도 `3.3.4` → `3.3.5`로 패치 레벨만 갱신(마이너/메이저 변경 없는 안전한 범위).
- Ktor 서버 라이브러리 버전(`2.3.12`)은 **의도적으로 안 건드림** — Ktor 3.x는 서버 설정 API가 바뀌어서, 버전만 올리고 `main.kt` 템플릿의 `embeddedServer(...)` 코드를 같이 안 바꾸면 생성된 프로젝트가 컴파일 자체가 안 되는 상태(현재의 "오래됐지만 동작함"보다 나쁜 상태)가 될 위험이 있음. 확인 없이 올리는 것보다 문서에 남기는 게 안전하다고 판단.
- C#/Rust 폴백(`net8.0`→`net9.0`)은 ASP.NET Core 문서 작업 중에 같이 갱신함.

## 남은 항목 (미결정)

Ktor 3.x 마이그레이션(버전 + `main.kt` 라우팅 코드 동시 수정), Kotlin 컴파일러 버전의 완전한 라이브 조회화는 별도 작업으로 남겨둠 — 필요하면 요청 바람.
