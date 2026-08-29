# Spring Boot (Kotlin)

Create a Spring Boot project with Kotlin via:

```bash
stoke init spring-boot-kotlin
```

Unlike the Java [Spring Boot](spring-boot.md) scaffold (which calls Spring Initializr), this generates a minimal Gradle Kotlin DSL project by hand — no network call required.

## Prompts

- **Project name**: directory name for the project

## Generated files

    myapp/
    ├── stoke.toml
    ├── settings.gradle.kts
    ├── build.gradle.kts
    ├── gradlew / gradlew.bat      # if `gradle` was found to generate the wrapper
    └── src/
        └── main/
            └── kotlin/
                └── myapp/
                    └── Application.kt   # @SpringBootApplication + a sample @RestController

## Dependencies

- `org.springframework.boot:spring-boot-starter-web`
- `org.jetbrains.kotlin:kotlin-reflect`
- Gradle plugins: `org.springframework.boot`, `io.spring.dependency-management`, `kotlin("jvm")`, `kotlin("plugin.spring")`

## Default settings

- **Port**: `8080` (Spring Boot's default)
- **Endpoints**:
  - `GET /` → `Hello from Spring Boot (Kotlin) + stoke!`
  - `GET /hello/{name}` → `Hello, {name}!`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8080/`

## Customization

- Change port: add `server.port=<port>` to `src/main/resources/application.properties` (create the file if it doesn't exist)
- Add endpoints: add `@GetMapping`/`@PostMapping` methods to `HomeController`, or add new `@RestController` classes
- Add dependencies: add Spring Boot starters (`spring-boot-starter-data-jpa`, etc.) to `build.gradle.kts`
