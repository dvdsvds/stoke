# 명령어 개요

stoke 명령어는 목적별로 정리되어 있습니다.

## 빌드 & 실행

| 명령어 | 설명 |
|---------|-------------|
| [`stoke build`](build.md) | 타깃 컴파일 |
| [`stoke run`](run.md) | 빌드된 타깃 실행 |
| [`stoke watch`](watch.md) | 파일 변경 시 자동 재빌드 |
| [`stoke hot-reload`](hot-reload.md) | 재빌드 + 프로세스 재시작 |

## 프로젝트 관리

| 명령어 | 설명 |
|---------|-------------|
| [`stoke init`](init.md) | 새 프로젝트 생성 |
| [`stoke clean`](clean.md) | 빌드 산출물 삭제 |
| [`stoke ide-sync`](ide-sync.md) | IDE 설정 생성 |

## 툴체인

| 명령어 | 설명 |
|---------|-------------|
| `stoke python list` | 감지된 Python 설치 목록 |
| `stoke java list` | 감지된 JDK 목록 |
| `stoke c list` | 감지된 C 컴파일러 목록 |
| `stoke cpp list` | 감지된 C++ 컴파일러 목록 |

## C/C++ 라이브러리

| 명령어 | 설명 |
|---------|-------------|
| `stoke install vcpkg` | vcpkg 설치 |
| `stoke uninstall vcpkg` | vcpkg 제거 |
| `stoke vcpkg install <lib>` | 라이브러리 설치 |
| `stoke vcpkg remove <lib>` | 라이브러리 제거 |
| `stoke vcpkg list` | 설치된 라이브러리 목록 |
| `stoke vcpkg version` | vcpkg 버전 표시 |

자세한 내용은 [vcpkg 가이드](../advanced/vcpkg.md)를 참고하세요.

## 전역 옵션

대부분의 명령어에서 사용 가능:

### `--verbose` (`-v`)

자세한 출력 표시:

```bash
stoke build --verbose
```

기본 출력은 간결합니다. verbose는 컴파일러 경로, 의존성 스캔, 파일별 진행 상황을 보여줍니다.

### 언어 선택

환경변수 `STOKE_LANG=ko`를 설정하면 도움말 메시지를 한국어로 볼 수 있습니다:

```bash
STOKE_LANG=ko stoke --help
```

기본값은 영어입니다. CLI 출력(빌드 진행, 에러)은 영어로 유지됩니다.

## 도움말 보기

각 명령어는 자체 도움말을 제공합니다:

```bash
stoke --help
stoke build --help
stoke vcpkg install --help
```
