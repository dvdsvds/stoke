# stoke

여러 언어로 프로젝트를 만들고, 빌드하고, 실행하는 도구
[← 메인 README로 돌아가기](../README.md) · [English](./README_en.md)

## 소개

`stoke.toml` 하나로 가상환경, 의존성, IDE 통합, 재현 가능한 빌드를 관리
Python, Java, C, C++, Go, JavaScript, TypeScript 프로젝트를 같은 인터페이스로 만들고, 빌드하고, 실행
Spring Boot, FastAPI, Flask, Django, 그리고 Go/JavaScript/TypeScript용 웹 프레임워크 12종 스캐폴딩 지원

## 주요 기능

- **다국어 지원** — Python, Java, C, C++, Go, JavaScript, TypeScript 통합 관리
- **언어 설치** — `stoke install --language=X`로 Python/JDK/gcc/Go/Node.js 자동 설치
- **프레임워크 스캐폴딩** — Spring Boot, FastAPI, Flask, Django, Gin, Echo, Fiber, Chi, Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono
- **Python 환경** — venv 또는 conda 선택 가능
- **자동 의존성 관리** — pip, Maven Central, vcpkg 통합
- **자동 IDE 통합** — VSCode, IntelliJ, Eclipse 설정 파일 자동 생성
- **Watch 모드 + Hot-reload** — 파일 변경 감지 후 자동 재빌드, 프로세스 재시작
- **빌드 프로파일** — C/C++용 debug/release 및 커스텀 프로파일 (컴파일 플래그, defines, 컴파일러 지정)
- **재현 가능한 빌드** — lock 파일 기반 팀 재현성
- **증분 빌드** — mtime 캐시로 안 바뀐 파일 skip
- **대화형 초기화** — `stoke init`으로 프로젝트 설정 생성

## 설치

### Windows (초심자 추천)
[Releases](https://github.com/dvdsvds/stoke/releases/latest)에서 인스톨러 다운로드. Python 포함되어 있어 별도 설치 필요 없음.

### pip (개발자용)
```bash
pip install stoke-build
```
pip 방식은 Python 3.11 이상 필요.

## 빠른 시작

```bash
mkdir myapp
cd myapp
stoke init
stoke build
stoke run
```

## 명령어

### 프로젝트 관리

| 명령어 | 설명 |
| --- | --- |
| `stoke init` | 대화형 프로젝트 초기화 (Python, Java, C, C++, Go, JavaScript, TypeScript) |
| `stoke init <framework>` | 프레임워크 프로젝트 바로 생성 ([프레임워크 스캐폴딩](#프레임워크-스캐폴딩) 참고) |
| `stoke build [target]` | 타겟 빌드 |
| `stoke build --force` | 캐시 무시하고 전체 재빌드 |
| `stoke build --debug` / `--release` / `--profile=<name>` | 특정 프로파일로 빌드 (C/C++) |
| `stoke run [target]` | 빌드된 타겟 실행 |
| `stoke watch [target]` | 파일 변경 감지 후 자동 재빌드 |
| `stoke hot-reload [target]` | 재빌드 + 실행 중인 프로세스 재시작 |
| `stoke clean [target]` | 빌드 산출물 삭제 |
| `stoke clean --all` | lock 파일 포함 완전 초기화 |
| `stoke ide-sync` | 워크스페이스 IDE 통합 파일 관리 |

### 언어별 도구

| 명령어 | 설명 |
| --- | --- |
| `stoke python list` | 설치된 파이썬 목록 |
| `stoke java list` | 설치된 JDK 목록 |
| `stoke c list` | 설치된 C 컴파일러 (gcc) |
| `stoke cpp list` | 설치된 C++ 컴파일러 (g++) |

### 도구 관리

| 명령어 | 설명 |
| --- | --- |
| `stoke install vcpkg` | vcpkg 설치 (`~/.stoke/tools/vcpkg/`) |
| `stoke uninstall vcpkg` | vcpkg 제거 |
| `stoke install --language=<lang> --version=<ver>` | 언어 툴체인 설치 (`python`, `java`, `c`, `cpp`, `go`, `nodejs`, `conda`; 기본 버전: `latest`) |
| `stoke install --language=<lang> --list` | 해당 언어의 설치 가능한 버전 목록 조회 |
| `stoke uninstall --language=<lang> --version=<ver>` | 설치된 툴체인 제거 (`python`, `java`, `c`, `cpp`, `go`, `conda`) |

### 프레임워크 스캐폴딩

`stoke init <framework>`로 즉시 실행 가능한 프레임워크 프로젝트를 생성합니다:

| 언어 | 프레임워크 |
| --- | --- |
| Java | `spring-boot` |
| Python | `fastapi`, `flask`, `django` |
| Go | `gin`, `echo`, `fiber`, `chi` |
| JavaScript | `express`, `fastify` |
| TypeScript | `nextjs`, `nestjs`, `vite`, `nuxt`, `sveltekit`, `hono` |

### C/C++ 라이브러리 관리 (vcpkg)

| 명령어 | 설명 |
| --- | --- |
| `stoke vcpkg install <library>` | 라이브러리 설치 (최신 버전) |
| `stoke vcpkg install <library> --version=X` | 특정 버전 설치 |
| `stoke vcpkg remove <library>` | 라이브러리 제거 |
| `stoke vcpkg list` | 설치된 라이브러리 목록 |
| `stoke vcpkg version` | vcpkg 버전 확인 |

## 언어별 설정 예시

### Python

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "python"
python_version = "3.12"
sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.myapp.deps]
requests = "2.31.0"
fastapi = ">=0.100.0"
```

### Java

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "java"
java_version = "21"
sources = ["src/**/*.java"]
main_class = "com.example.Main"

[targets.myapp.deps]
"com.google.code.gson:gson" = "2.10.1"
```

### C

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "c"
c_standard = "c17"
sources = ["src/**/*.c"]
```

### C++

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "cpp"
cpp_standard = "c++17"
sources = ["src/**/*.cpp"]

[targets.myapp.deps]
fmt = "latest"
```

### Go

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "go"
```

의존성은 `stoke.toml`이 아니라 `go.mod`로 관리합니다.

### JavaScript

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "javascript"
entry = "src/main.js"
```

의존성은 `package.json`으로 관리합니다 (`stoke build` 실행 시 `npm install` 수행).

### TypeScript

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"

[targets.myapp]
language = "typescript"
entry = "src/main.ts"
```

`tsx`로 실행됩니다. 의존성은 `package.json`으로 관리합니다.

## Lock 파일 모드

- **`commit`** — 프로젝트 루트에 `stoke.lock`, git 커밋 대상 (팀 재현성)
- **`local`** — `.stoke/lock.toml`, gitignore 대상 (개발자별 관리)

## 의존성 버전 문법

### Python (pip specifier)

- `"2.31.0"` — 정확한 버전
- `">=2.0.0"`, `"<3.0.0"` — 버전 범위
- `"*"` 또는 `""` — 아무 버전

### Java (Maven 좌표)

- `"groupId:artifactId" = "version"`
- 예시: `"com.google.code.gson:gson" = "2.10.1"`

### C/C++ (vcpkg)

- `"latest"` — 최신 버전 (기본값)
- `"10.2.1"` — 특정 버전

## IDE 통합

### Python

- `.vscode/settings.json` — 파이썬 인터프리터 경로

### Java

- `.classpath`, `.project` — Eclipse, VSCode Java 확장
- `pom.xml` — IntelliJ IDEA, Maven 기반 IDE
- `.vscode/settings.json` — 참조 라이브러리

### C / C++

- `compile_commands.json` — clangd, VSCode C/C++ 확장, CLion
- `.vscode/c_cpp_properties.json` — VSCode C/C++ 확장

### Go / JavaScript / TypeScript

stoke가 관리하는 IDE 파일은 아직 없습니다 — 각 언어의 에디터 툴링(`gopls`, 내장 TS/JS 언어 서비스)을 그대로 사용합니다.

### 워크스페이스 (여러 프로젝트)

`stoke ide-sync` 실행 시 워크스페이스 루트에 `<폴더이름>.code-workspace` 생성

VSCode에서 `File > Open Workspace from File`로 열면 각 프로젝트가 독립된 root로 인식

## 동작 방식

`stoke build` 실행 시:

1. `stoke.toml` 파싱 후 타겟 결정
2. 언어별 처리:
   - Python: venv 생성 → pip 의존성 설치 → 문법 체크
   - Java: JDK 감지 → Maven 의존성 다운로드 → `javac` 컴파일
   - C/C++: 컴파일러 감지 → vcpkg 의존성 설치 → `gcc`/`g++` 컴파일 + 링크
   - Go: `go` 툴체인 감지 → `go build`
   - JavaScript/TypeScript: Node.js 감지 → `npm install` (`package.json`이 있을 때)
3. IDE 통합 파일 생성 (`.classpath`, `pom.xml`, `compile_commands.json` 등, Python/Java/C/C++ 대상)
4. `.gitignore` 자동 관리
5. lock 파일 저장 (변경 시에만)
6. 캐시 저장 (`.stoke/cache.json`)

## Python 프로젝트 설정

### Entry 파일 지정

`stoke.toml`의 `entry` 필드는 실행할 파이썬 파일의 경로입니다. 기본값은 `src/main.py`입니다.

파일 이름이나 위치를 바꾸려면 `stoke.toml`을 직접 수정하세요:

```toml
[targets.myapp]
entry = "src/myapp/main.py"        # 커스텀 위치
# entry = "src/computer_main.py"   # 커스텀 이름
```

### 프로젝트 구조 관행

파이썬은 하위 폴더의 모듈을 사용하려면 명시적인 경로가 필요합니다.

**폴더 구조**:
src/
├── main.py
└── computer/
├── init.py
└── hardware/
├── init.py
└── cpu.py

**main.py의 import**:
```python
from computer.hardware.cpu import CPU
```

**주의**:
- 각 하위 폴더에 `__init__.py`가 있어야 함 (빈 파일도 됨)
- 짧은 이름 (`from cpu import CPU`)은 안 됩니다. 폴더 경로가 필요합니다.

## 로드맵
- **v0.1** — Python 빌드 (venv, 의존성, 문법 체크, 증분 빌드)
- **v0.2** — Watch 모드, hot-reload
- **v0.3** — Java 지원 (JDK 감지, Maven Central, IDE 통합)
- **v0.4** — C/C++ 지원 (gcc/g++, watch, hot-reload, IDE 통합)
- **v0.5** — vcpkg 통합, 도구 관리, multi-root workspace
- **v0.6** — C/C++ 빌드 개선 (헤더 의존성 자동 추적, 병렬 컴파일, IDE 통합 자동화)
- **v0.7** — 빌드 프로파일 시스템 (debug/release, 커스텀 프로파일, clang 지원)
- **v0.8** — CLI help 한국어 지원 (STOKE_LANG 환경변수), 내부 리팩토링
- **v1.0** — 언어 설치 기능
  - CLI: `stoke install --language=X --version=Y`
  - 자체 버전 API (GitHub Pages)
  - Python, Java, C/C++ 지원
- **v1.1** — Go 언어 지원 (설치, 빌드, 실행, 제거), Go 프레임워크 스캐폴딩 (Gin, Echo, Fiber, Chi)
- **v1.2** — Node.js 설치 지원
- **v1.3** — JavaScript, TypeScript 지원, 웹 프레임워크 8종 추가 (Express, Fastify, Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono)

## 라이선스

MIT