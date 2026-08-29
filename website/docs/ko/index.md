# stoke

**여러 언어의 프로젝트를 빌드하고, 실행하고, 스캐폴딩하세요.**

stoke는 Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript 프로젝트의 개발 워크플로우를 하나로 통일합니다. 빌드, 실행, watch, 스캐폴딩을 위한 단일 커맨드라인 인터페이스 — Spring Boot, FastAPI, Flask, Django, Gin, Express, Next.js, Actix-web, Ktor, ASP.NET Core 등 인기 프레임워크도 지원합니다. `stoke.toml` 하나로 프로젝트를 설정하면, stoke가 컴파일·의존성 관리·IDE 연동 등을 알아서 처리합니다.

## 특징

- **다중 언어**: Python, Java, C, C++, Go, Rust, Kotlin, C#, Ruby, PHP, JavaScript, TypeScript 프로젝트를 같은 명령어로 빌드
- **언어 설치**: `stoke install`로 Python/JDK/gcc/Go/Node.js 설치
- **프레임워크 스캐폴딩**: Spring Boot, FastAPI, Flask, Django, 그리고 Go, JavaScript, TypeScript, Rust, Kotlin, C#, Ruby, PHP용 웹 프레임워크
- **Python 환경**: venv 또는 conda
- **빠름**: 헤더 의존성 추적을 통한 증분 컴파일
- **간단함**: 프로젝트 전체를 위한 `stoke.toml` 하나
- **Watch 모드**: 파일 변경 시 자동 재빌드
- **Hot-reload**: 재빌드 시 프로세스 재시작
- **IDE 연동**: VSCode/Eclipse/IntelliJ 설정 자동 생성
- **빌드 프로파일**: Debug/Release/커스텀 프로파일
- **의존성 관리**: Python은 pip, Java는 Maven, C/C++는 vcpkg, Go는 go.mod, Rust는 Cargo, Kotlin은 Gradle, C#은 NuGet, Ruby는 Bundler, PHP는 Composer, JavaScript/TypeScript는 npm

## 간단한 예시

`stoke.toml` 생성:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]
```

빌드하고 실행:

```bash
stoke build
stoke run
```

끝입니다.

## 시작하기

- [설치](getting-started/installation.md) — Windows/Linux/macOS에 stoke 설치하기
- [빠른 시작](getting-started/quick-start.md) — 첫 프로젝트 빌드하기

## 문서 목차

- [명령어](commands/overview.md) — build, run, watch 등
- [언어](languages/python.md) — 언어별 가이드
- [설정](configuration/stoke-toml.md) — `stoke.toml` 레퍼런스
- [고급](advanced/vcpkg.md) — vcpkg, IDE 연동

## 링크

- **GitHub**: [github.com/dvdsvds/stoke](https://github.com/dvdsvds/stoke)
- **릴리스**: [최신 버전](https://github.com/dvdsvds/stoke/releases)
