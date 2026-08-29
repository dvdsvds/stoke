# stoke watch

파일 변경을 감지해서 자동으로 재빌드합니다.

## 사용법

```bash
stoke watch [target] [options]
```

## 옵션

| 옵션 | 설명 |
|--------|-------------|
| `--debug` | Debug 빌드 (기본값) |
| `--release` | Release 빌드 |
| `--profile <name>` | 커스텀 프로파일 |
| `-v`, `--verbose` | 자세한 빌드 출력 표시 |

## 예시

```bash
stoke watch
```

출력:
==================================================
[watch] Rebuilding 'myapp'...
Using c compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp
[watch] Watching: C:\myproject\src
[watch] Press Ctrl+C to stop.

파일을 저장하면 stoke가 자동으로 재빌드합니다:
[watch] Detected changes in: src\main.c
==================================================
[watch] Rebuilding 'myapp'...
Using c compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp

Ctrl+C로 중지합니다.

## 감시 대상

stoke는 `sources` 패턴이 가리키는 디렉토리를 감시합니다. 예를 들어:

```toml
[targets.myapp]
sources = ["src/**/*.c"]
```

이면 stoke는 `src/`를 감시합니다.

언어에 맞는 소스 확장자와 일치하는 파일만 대상이 됩니다:

- **Python**: `.py`
- **Java**: `.java`
- **C**: `.c`, `.h`
- **C++**: `.cpp`, `.hpp`, `.h`

그 외 파일 변경은 무시됩니다.

## 디바운싱

빠르게 연속된 여러 변경은 디바운싱됩니다. 파일 5개를 연달아 저장해도 stoke는 5번이 아니라 한 번만 재빌드합니다.

## 프로파일과 함께 사용

watch는 선택한 프로파일을 그대로 따릅니다:

```bash
stoke watch --release
```

변경이 있을 때마다 `.stoke/{lang}/{target}/release/`에 빌드합니다.

## 관련 문서

- [`stoke hot-reload`](hot-reload.md) — watch + 프로세스 재시작
- [`stoke build`](build.md) — 단일 빌드
