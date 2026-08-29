# 빠른 시작

첫 stoke 프로젝트를 만들고 빌드하는 과정을 안내합니다.

## 새 프로젝트 생성

`stoke init`으로 대화형으로 새 프로젝트를 스캐폴딩하세요:

```bash
mkdir myapp
cd myapp
stoke init
```

마법사가 다음을 물어봅니다:

- 프로젝트 이름
- 언어 (Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript)
- 버전 요구사항
- 의존성

생성되는 것:

- `stoke.toml` — 프로젝트 설정
- `src/` — hello-world 파일이 있는 소스 디렉토리

## 빌드

```bash
stoke build
```

출력:
Building 'myapp' (cpp)...
Using cpp compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp

빌드 산출물은 `.stoke/`에 생성됩니다.

## 실행

```bash
stoke run
```

출력:
Running: ...\myapp.exe
Hello from stoke!

## Watch 모드

파일 변경 시 자동 재빌드:

```bash
stoke watch
```

Ctrl+C로 중지합니다.

## Hot-reload

자동으로 재빌드하고 프로세스를 재시작:

```bash
stoke hot-reload
```

서버나 장시간 실행되는 프로세스에 유용합니다.

## 언어별 빠른 시작

### Python

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "python"
python_version = "3.12"
entry = "src/main.py"

[targets.myapp.deps]
requests = "*"
```

```bash
stoke build     # Creates venv, installs deps
stoke run       # Runs src/main.py
```

### Java

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "java"
java_version = "25"
sources = ["src/main/java/**/*.java"]
main_class = "com.example.Main"
```

```bash
stoke build     # Compiles .java files
stoke run       # Runs main_class
```

### C

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "c"
sources = ["src/**/*.c"]
```

```bash
stoke build     # Compiles + links
stoke run       # Runs the executable
```

### C++

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]
```

```bash
stoke build
stoke run
```

### Go

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "go"
```

```bash
stoke build     # go build
stoke run       # runs the compiled binary
```

### Rust

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "rust"
```

```bash
stoke build     # cargo build --release
stoke run       # runs the compiled binary
```

### Kotlin

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "kotlin"
java_version = "21"
```

```bash
stoke build     # gradlew build -x test
stoke run       # gradlew run (needs the application plugin)
```

### C#

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "csharp"
```

```bash
stoke build     # dotnet build
stoke run       # runs the built binary
```

### Ruby

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "ruby"
entry = "src/main.rb"
```

```bash
stoke build     # bundle install (if Gemfile exists)
stoke run       # ruby src/main.rb (or bundle exec ruby)
```

### PHP

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "php"
entry = "src/main.php"
```

```bash
stoke build     # composer install (if composer.json exists)
stoke run       # php src/main.php
```

### JavaScript

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "javascript"
entry = "src/main.js"
```

```bash
stoke build     # npm install (if package.json exists)
stoke run       # node src/main.js
```

### TypeScript

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "typescript"
entry = "src/main.ts"
```

```bash
stoke build     # npm install
stoke run       # runs src/main.ts via tsx
```

## 다음 단계

- [명령어 레퍼런스](../commands/overview.md)
- [`stoke.toml` 레퍼런스](../configuration/stoke-toml.md)
- 언어 가이드: [Python](../languages/python.md), [Java](../languages/java.md), [C/C++](../languages/cpp.md), [Go](../languages/go.md), [Rust](../languages/rust.md), [Kotlin](../languages/kotlin.md), [C#](../languages/csharp.md), [Ruby](../languages/ruby.md), [PHP](../languages/php.md), [JavaScript](../languages/javascript.md), [TypeScript](../languages/typescript.md)
