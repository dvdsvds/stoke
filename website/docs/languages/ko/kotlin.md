# Kotlin

stoke는 Gradle에 위임하는 방식으로 Kotlin 프로젝트를 지원합니다 (프로젝트의 Gradle Wrapper, 또는 시스템에 설치된 `gradle` 사용).

## 요구사항

- JDK ([Java](java.md)와 동일한 감지 로직 재사용)
- 프로젝트 내 Gradle Wrapper(`gradlew`), 또는 PATH의 시스템 `gradle`

## 설정

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "kotlin"
java_version = "21"
```

## 동작 방식

- `stoke build`는 `gradlew build -x test` 실행 (빠른 루프를 위해 테스트 스킵)
- `stoke run`은 `gradlew run` 실행 — `build.gradle.kts`에 Gradle `application` 플러그인과 `mainClass` 설정 필요
- 프로젝트에 `gradlew`가 없으면 시스템에 설치된 `gradle`로 대체
- `--force`는 `gradlew build --rerun-tasks`로 매핑됨

## 예시

새 Kotlin 프로젝트 생성:

```bash
mkdir myapp
cd myapp
stoke init
```

언어 메뉴에서 `Kotlin` 선택. stoke가:

- `stoke.toml` 생성
- `settings.gradle.kts`, `build.gradle.kts`, `src/main/kotlin/Main.kt` 생성
- `gradle`이 있으면 `gradle wrapper` 실행해서 `gradlew` 생성

그 다음:

```bash
stoke build
stoke run
```

## 프레임워크 스캐폴딩

```bash
stoke init ktor                 # Ktor — 경량, 코루틴 기반 프레임워크
stoke init spring-boot-kotlin   # Kotlin DSL + kotlin-spring 플러그인 사용 Spring Boot
```

자세한 내용은 [Frameworks](../../frameworks/ko/overview.md) 참조.

## 참고

- 빌드 결과물은 Gradle 기본 `build/` 디렉토리(프로젝트 루트)를 사용 — 다른 언어처럼 `.stoke/kotlin/<target>`이 아님. `stoke clean`도 이걸 알고 `build/`를 대신 삭제함
- `.stoke/`와 함께 `build/`, `.gradle/`도 `.gitignore`에 자동 추가됨
- `stoke.toml`의 `java_version`은 참고용일 뿐 — 실제 사용되는 JDK는 Gradle 자체 툴체인 해석(또는 `JAVA_HOME`)을 따름
