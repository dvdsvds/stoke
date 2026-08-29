# stoke run

빌드된 타깃을 실행합니다.

## 사용법

```bash
stoke run [target] [options]
```

`target`을 생략하면 `stoke.toml`의 첫 번째 타깃이 사용됩니다.

`stoke run`은 재빌드를 **하지 않습니다**. 이전에 빌드된 산출물을 실행합니다. 변경했다면 먼저 `stoke build`를 실행하세요.

## 옵션

| 옵션 | 설명 |
|--------|-------------|
| `--debug` | debug 빌드 실행 (기본값) |
| `--release` | release 빌드 실행 |
| `--profile <name>` | 특정 커스텀 프로파일 빌드 실행 |

## 예시

### 기본 실행

```bash
stoke run
```

기본 타깃을 debug 프로파일로 실행합니다.

### 타깃 지정

```bash
stoke run myapp
```

### Release 빌드 실행

```bash
stoke build --release
stoke run --release
```

### 커스텀 프로파일 실행

```bash
stoke build --profile=small
stoke run --profile=small
```

## 언어별 동작

### Python

프로젝트의 venv로 `entry` 스크립트를 실행합니다:

```toml
[targets.myapp]
language = "python"
entry = "src/main.py"
```
$ stoke run
Running: C:\myproject\src\main.py
Hello from stoke!

### Java

`main_class`로 지정된 클래스를 실행합니다:

```toml
[targets.myapp]
language = "java"
main_class = "com.example.Main"
```
$ stoke run
Running: com.example.Main
Hello from stoke!

클래스패스에는 컴파일된 `.class` 파일과 Maven 의존성이 포함됩니다.

### C / C++

컴파일된 실행 파일을 실행합니다:
$ stoke run
Running: .stoke\cpp\myapp\debug\myapp.exe
Hello from stoke!

## 종료 코드

`stoke run`의 종료 코드는 타깃의 종료 코드와 일치합니다. 프로그램이 0이 아닌 값을 반환하면 `stoke run`도 0이 아닌 값을 반환합니다.

## 관련 문서

- [`stoke build`](build.md) — 실행 전 빌드
- [`stoke hot-reload`](hot-reload.md) — 파일 변경 시 재빌드 및 재시작
