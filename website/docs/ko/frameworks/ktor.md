# Ktor

Ktor 프로젝트 생성:

```bash
stoke init ktor
```

Ktor는 JetBrains가 만든 경량, 코루틴 기반 Kotlin 웹 프레임워크입니다.

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
                └── Main.kt        # Ktor 진입점

## 의존성

- `io.ktor:ktor-server-core-jvm` `2.3.12`
- `io.ktor:ktor-server-netty-jvm` `2.3.12` (Netty 엔진)

## 기본 설정

- **Port**: `8080`
- **Endpoints**:
  - `GET /` → `Hello from Ktor + stoke!`
  - `GET /hello/{name}` → `Hello, {name}!`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:8080/`

## 커스터마이징

- 포트 변경: `src/main/kotlin/Main.kt`의 `embeddedServer(Netty, port = 8080)` 수정
- 라우트 추가: `routing { ... }` 블록 안에 추가
- 플러그인 추가: `embeddedServer { ... }` 안에서 Ktor 플러그인(`ContentNegotiation`, `CORS` 등) 설치
