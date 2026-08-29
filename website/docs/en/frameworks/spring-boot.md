# Spring Boot

Create a Spring Boot project via:

```bash
stoke init spring-boot
```

This uses [Spring Initializr](https://start.spring.io/) API to download a standard Spring Boot project.

## Prompts

- **Project name**: directory name for the project
- **Group ID**: Maven groupId (e.g. `com.example`)
- **Spring Boot version**: selected from available RELEASE versions (fetched from Spring Initializr)
- **Java version**: 17, 21, or 25
- **Build tool**: Maven or Gradle
- **Packaging**: jar or war
- **Dependencies**: comma-separated (e.g. `web,data-jpa,security`)

### Common dependencies

| ID | Description |
| --- | --- |
| `web` | Spring Web (REST API) |
| `data-jpa` | Spring Data JPA |
| `security` | Spring Security |
| `actuator` | Spring Boot Actuator |
| `devtools` | Spring Boot DevTools |
| `lombok` | Lombok |
| `h2` | H2 Database |
| `postgresql` | PostgreSQL Driver |

## Generated files (Maven)

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

## Notes

- stoke does not build or run Spring Boot projects. Use Maven or Gradle after scaffolding.
- The Spring Initializr API returns versions with a `.RELEASE` suffix (e.g. `4.1.0.RELEASE`), but Maven Central uses plain versions (e.g. `4.1.0`). stoke strips the `.RELEASE` suffix automatically.

## Run

```bash
cd myapp
mvnw spring-boot:run        # Linux/macOS
mvnw.cmd spring-boot:run    # Windows
```

Or with Gradle:

```bash
gradlew bootRun             # Linux/macOS
gradlew.bat bootRun         # Windows
```

Default port: `8080`

Open `http://localhost:8080/`

## Customization

Standard Spring Boot project — refer to [Spring Boot documentation](https://docs.spring.io/spring-boot/) for configuration.