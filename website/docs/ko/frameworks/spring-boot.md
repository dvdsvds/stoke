# Spring Boot

Spring Boot 프로젝트 생성:

```bash
stoke init spring-boot
```

[Spring Initializr](https://start.spring.io/) API를 사용해서 표준 Spring Boot 프로젝트 다운로드.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름
- **Group ID**: Maven groupId (예: `com.example`)
- **Spring Boot version**: 사용 가능한 RELEASE 버전 중 선택 (Spring Initializr에서 조회)
- **Java version**: 17, 21, 25
- **Build tool**: Maven 또는 Gradle
- **Packaging**: jar 또는 war
- **Dependencies**: 콤마로 구분 (예: `web,data-jpa,security`)

### 자주 사용하는 의존성

| ID | 설명 |
| --- | --- |
| `web` | Spring Web (REST API) |
| `data-jpa` | Spring Data JPA |
| `security` | Spring Security |
| `actuator` | Spring Boot Actuator |
| `devtools` | Spring Boot DevTools |
| `lombok` | Lombok |
| `h2` | H2 Database |
| `postgresql` | PostgreSQL Driver |

## 생성 파일 (Maven)

    myapp/
    ├── pom.xml
    ├── mvnw
    ├── mvnw.cmd
    ├── .mvn/
    │   └── wrapper/
    │       └── maven-wrapper.properties
    └── src/
        ├── main/
        │   ├── java/
        │   │   └── com/example/myapp/
        │   │       └── MyappApplication.java
        │   └── resources/
        │       ├── application.properties
        │       ├── static/
        │       └── templates/
        └── test/
            └── java/
                └── com/example/myapp/
                    └── MyappApplicationTests.java

## 참고 사항

- stoke는 Spring Boot 프로젝트를 빌드하거나 실행하지 않음. 스캐폴딩 후 Maven 또는 Gradle 사용.
- Spring Initializr API는 `.RELEASE` 접미사가 붙은 버전 반환 (예: `4.1.0.RELEASE`). Maven Central은 접미사 없는 버전만 사용 (예: `4.1.0`). stoke가 `.RELEASE` 접미사를 자동으로 제거.

## 실행

```bash
cd myapp
mvnw spring-boot:run        # Linux/macOS
mvnw.cmd spring-boot:run    # Windows
```

Gradle 사용 시:

```bash
gradlew bootRun             # Linux/macOS
gradlew.bat bootRun         # Windows
```

기본 포트: `8080`

브라우저: `http://localhost:8080/`

## 커스터마이징

표준 Spring Boot 프로젝트 — 설정은 [Spring Boot 공식 문서](https://docs.spring.io/spring-boot/) 참조.