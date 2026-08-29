# Spring Boot (Kotlin)

Kotlin 기반 Spring Boot 프로젝트 생성:

```bash
stoke init spring-boot-kotlin
```

Java용 [Spring Boot](spring-boot.md) 스캐폴딩(Spring Initializr 호출)과 달리, 이건 네트워크 호출 없이 최소 Gradle Kotlin DSL 프로젝트를 직접 생성합니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── settings.gradle.kts
    ├── build.gradle.kts
    ├── gradlew / gradlew.bat      # gradle이 있으면 wrapper 생성
    └── src/
        └── main/
            └── kotlin/
                └── myapp/
                    └── Application.kt   # @SpringBootApplication + 샘플 @RestController

## 의존성

- `org.springframework.boot:spring-boot-starter-web`
- `org.jetbrains.kotlin:kotlin-reflect`
- Gradle 플러그인: `org.springframework.boot`, `io.spring.dependency-management`, `kotlin("jvm")`, `kotlin("plugin.spring")`

## 기본 설정

- **Port**: `8080` (Spring Boot 기본값)
- **Endpoints**:
  - `GET /` → `Hello from Spring Boot (Kotlin) + stoke!`
  - `GET /hello/{name}` → `Hello, {name}!`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:8080/`

## 커스터마이징

- 포트 변경: `src/main/resources/application.properties`에 `server.port=<port>` 추가 (파일이 없으면 새로 생성)
- 엔드포인트 추가: `HomeController`에 `@GetMapping`/`@PostMapping` 메서드 추가, 또는 새 `@RestController` 클래스 추가
- 의존성 추가: `build.gradle.kts`에 Spring Boot 스타터(`spring-boot-starter-data-jpa` 등) 추가
