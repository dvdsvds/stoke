# Kotlin

stoke supports Kotlin projects by delegating to Gradle (via the project's Gradle Wrapper, or a system-installed `gradle`).

## Requirements

- A JDK (reuses the same detection as [Java](java.md))
- Gradle Wrapper in the project (`gradlew`), or system `gradle` on PATH

## Configuration

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "kotlin"
java_version = "21"
```

## How it works

- `stoke build` runs `gradlew build -x test` (skips tests for a faster loop)
- `stoke run` runs `gradlew run` — requires the Gradle `application` plugin with `mainClass` set in `build.gradle.kts`
- If no `gradlew` is found in the project, stoke falls back to a system-installed `gradle`
- `--force` maps to `gradlew build --rerun-tasks`

## Example

Create a new Kotlin project:

```bash
mkdir myapp
cd myapp
stoke init
```

Select `Kotlin` from the language menu. stoke will:

- Create `stoke.toml`
- Generate `settings.gradle.kts`, `build.gradle.kts`, and `src/main/kotlin/Main.kt`
- Run `gradle wrapper` if `gradle` is available, to generate `gradlew`

Then:

```bash
stoke build
stoke run
```

## Framework scaffolding

```bash
stoke init ktor                 # Ktor — lightweight, coroutine-based framework
stoke init spring-boot-kotlin   # Spring Boot with Kotlin DSL + kotlin-spring plugin
```

See [Frameworks](../../frameworks/en/overview.md) for details.

## Notes

- Build output uses Gradle's own default `build/` directory at the project root (not `.stoke/kotlin/<target>` like other languages) — `stoke clean` knows to remove `build/` instead
- `build/` and `.gradle/` are added to `.gitignore` alongside `.stoke/`
- `java_version` in `stoke.toml` is informational only; the actual JDK used is whatever Gradle picks up (its own toolchain resolution, or `JAVA_HOME`)
