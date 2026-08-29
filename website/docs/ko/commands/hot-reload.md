# stoke hot-reload

파일 변경을 감지해서 재빌드하고, 실행 중인 프로세스를 재시작합니다.

## 사용법

```bash
stoke hot-reload [target] [options]
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
stoke hot-reload
```

출력:
==================================================
[hot-reload] Rebuilding 'myapp'...
Using c compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp
[hot-reload] Starting: .stoke\cpp\myapp\debug\myapp.exe
[hot-reload] Watching: C:\myproject\src
[hot-reload] Press Ctrl+C to stop.
Hello from stoke!

파일을 저장하면 stoke가 프로세스를 멈추고, 재빌드한 뒤, 다시 시작합니다:
[hot-reload] Detected changes in: src\main.c
[hot-reload] Stopping process...
==================================================
[hot-reload] Rebuilding 'myapp'...
Using c compiler 15.2.0
Compiled 1 file(s)
Build complete: myapp
[hot-reload] Starting: .stoke\cpp\myapp\debug\myapp.exe
Hello from stoke!

Ctrl+C로 watcher와 프로세스를 모두 중지합니다.

## 사용 시기

장시간 실행되는 프로세스에 가장 적합합니다:

- 웹 서버 (Flask, Spring Boot 등)
- 상태를 가진 개발용 스크립트
- 백그라운드 워커

금방 끝나고 종료되는 배치 프로그램이라면 보통 `stoke watch`로 충분합니다.

## 언어별 동작

[`stoke run`](run.md)과 동일합니다:

- **Python**: `entry` 스크립트 실행
- **Java**: `main_class` 실행
- **C/C++**: 컴파일된 실행 파일 실행

## C/C++ 참고사항

C/C++의 경우 stoke는 재빌드하기 **전에** 프로세스를 멈춥니다. 대부분의 플랫폼에서 링커가 실행 중인 실행 파일을 덮어쓸 수 없기 때문에 필요한 과정입니다.

Python과 Java는 이런 제약이 없어서, stoke가 먼저 재빌드하고 그 이후에 프로세스를 멈춥니다.

## 관련 문서

- [`stoke watch`](watch.md) — 재빌드만 하고 재시작은 안 함
- [`stoke run`](run.md) — 단일 실행
