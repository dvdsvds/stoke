# stoke clean

빌드 산출물을 삭제합니다.

## 사용법

```bash
stoke clean [target] [options]
```

`target`을 생략하면 모든 타깃이 정리됩니다.

## 옵션

| 옵션 | 설명 |
|--------|-------------|
| `--all` | 락 파일도 함께 삭제 (완전 초기화) |

## 예시

### 모든 타깃 정리

```bash
stoke clean
```

삭제 대상:

- 각 타깃의 `.stoke/{language}/{target}/` (Kotlin은 예외 — 프로젝트 루트의 Gradle 자체 `build/` 디렉토리를 사용하며, 이것도 `stoke clean`이 함께 삭제)
- `.stoke/cache.json`
- 프로젝트 내 모든 `__pycache__` 폴더

### 특정 타깃 정리

```bash
stoke clean myapp
```

`myapp`의 산출물만 삭제합니다.

### 완전 초기화

```bash
stoke clean --all
```

`.stoke/lock.toml`도 함께 삭제해서, 다음 빌드 때 의존성을 다시 해석하도록 강제합니다.

이럴 때 사용하세요:
- 락 파일이 손상됐을 때
- 의존성을 최신 버전으로 가져오고 싶을 때
- Python/JDK 버전을 바꿨다가 문제가 생겼을 때

## 삭제되는 것

| 항목 | `clean` | `clean --all` |
|------|---------|---------------|
| 오브젝트 파일 (`.o`, `.class`) | ✓ | ✓ |
| 실행 파일 | ✓ | ✓ |
| Python venv | ✓ | ✓ |
| `.stoke/cache.json` | ✓ | ✓ |
| `__pycache__/` | ✓ | ✓ |
| `.stoke/lock.toml` | | ✓ |
| IDE 파일 (`.vscode/`, `.classpath` 등) | | |

IDE 파일은 절대 삭제되지 않습니다. 다음 빌드 때 다시 생성됩니다.

## 정리 후

다음 빌드는:

- 전체 재컴파일 (캐시 없음)
- Python venv 재생성 (해당하는 경우)
- 의존성 재설치 (`--all` 사용 시)

## 관련 문서

- [`stoke build --force`](build.md) — 산출물을 지우지 않고 강제 재빌드
