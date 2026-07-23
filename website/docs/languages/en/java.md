# Java

stoke handles Java projects with JDK detection, incremental compilation, and Maven dependency management.

## Example `stoke.toml`

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "java"
java_version = "25"
sources = ["src/main/java/**/*.java"]
main_class = "com.example.Main"

[targets.myapp.deps]
"com.google.code.gson:gson" = "2.10.1"
"org.slf4j:slf4j-api" = "2.0.9"
```

## Target fields

| Field | Required | Description |
|-------|----------|-------------|
| `language` | Yes | Must be `"java"` |
| `java_version` | No | Required JDK major version (e.g. `"25"`) |
| `sources` | Yes | Glob patterns for `.java` files |
| `main_class` | Yes for `run` | Fully qualified main class |
| `deps` | No | Maven coordinates → version |

## JDK detection

Set `java_version` to require a specific major version:

```toml
java_version = "25"        # requires JDK 25 (any minor)
java_version = "17.0.13"   # requires exactly 17.0.13
```

stoke searches for a matching JDK in:

1. `JAVA_HOME` environment variable
2. `PATH` (`javac`)
3. Common installation paths:
   - Windows: `C:\Program Files\Eclipse Adoptium`, `C:\Program Files\Java`, `Zulu`, `Amazon Corretto`, `Microsoft`
   - macOS: `/Library/Java/JavaVirtualMachines`
   - Linux: `/usr/lib/jvm`, `/opt/java`

Check detected JDKs:

```bash
stoke java list
```

## Compilation

`stoke build` runs `javac` on all files matching `sources`.

Output: `.stoke/java/{target}/{profile}/classes/`

Incremental: only changed `.java` files are recompiled.

## Dependencies (Maven)

Declare dependencies with Maven coordinates (`groupId:artifactId`):

```toml
[targets.myapp.deps]
"com.google.code.gson:gson" = "2.10.1"
"org.junit.jupiter:junit-jupiter" = "5.10.0"
```

stoke downloads JAR files from Maven Central and caches them locally.

Locked versions and SHA1 hashes are stored in `.stoke/lock.toml`.

## Running

```bash
stoke run
```

Runs `java -cp <classpath> <main_class>`. The classpath includes:

- `.stoke/java/{target}/{profile}/classes/`
- All Maven dependency JARs

## Source layout

Standard Maven convention:
myapp/
├── stoke.toml
└── src/
└── main/
└── java/
└── com/
└── example/
├── Main.java
└── Utils.java

You can use any layout; adjust the `sources` glob to match:

```toml
sources = ["src/**/*.java"]              # any location under src/
sources = ["src/main/java/**/*.java"]    # Maven convention
```

## IDE integration

`stoke build` generates:

- `.classpath` — Eclipse project format
- `.project` — Eclipse project descriptor
- `.vscode/settings.json` — VSCode Java extension config
- `pom.xml` — Maven POM for IntelliJ / Maven-based tools

Open the project in Eclipse, VSCode (with Java extension pack), or IntelliJ — no extra setup needed.

## UTF-8 encoding

stoke sets `javac -encoding UTF-8` automatically. Source files with non-ASCII characters (Korean, Japanese, emoji, etc.) compile without issues.

## Related

- [`stoke build`](../commands/build.md)
- [`stoke run`](../commands/run.md)