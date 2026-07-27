# Ktor

Create a Ktor project via:

```bash
stoke init ktor
```

Ktor is a lightweight, coroutine-based web framework for Kotlin, built by JetBrains.

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
                └── Main.kt        # Ktor entry point

## Dependencies

- `io.ktor:ktor-server-core-jvm` `2.3.12`
- `io.ktor:ktor-server-netty-jvm` `2.3.12` (Netty engine)

## Default settings

- **Port**: `8080`
- **Endpoints**:
  - `GET /` → `Hello from Ktor + stoke!`
  - `GET /hello/{name}` → `Hello, {name}!`

## Run

```bash
cd myapp
stoke build
stoke run
```

Open `http://localhost:8080/`

## Customization

- Change port: edit `embeddedServer(Netty, port = 8080)` in `src/main/kotlin/Main.kt`
- Add routes: add entries inside the `routing { ... }` block
- Add plugins: install Ktor plugins (`ContentNegotiation`, `CORS`, etc.) inside `embeddedServer { ... }`
