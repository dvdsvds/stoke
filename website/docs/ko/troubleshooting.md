# 문제 해결

자주 발생하는 문제와 해결 방법입니다.

## 빌드 에러

### `stoke.toml not found`

**원인**: 프로젝트 디렉토리 밖에서 stoke를 실행했습니다.

**해결**: `stoke.toml`이 있는 프로젝트 루트로 `cd` 하세요.

### `target 'X' not found in stoke.toml`

**원인**: 지정한 타깃이 존재하지 않습니다.

**해결**: `stoke.toml`을 열어서 유효한 타깃을 확인하세요. 에러 출력에도 사용 가능한 타깃이 표시됩니다.

### `profile 'X' not found`

**원인**: 커스텀 프로파일이 `stoke.toml`에 없습니다.

**해결**: `stoke.toml`의 `[profiles.*]` 섹션을 확인하세요. `debug`, `release`, 그리고 직접 정의한 커스텀 프로파일만 유효합니다.

### `Python X.Y not found`

**원인**: `python_version`과 일치하는 Python이 설치되어 있지 않습니다.

**해결**:

1. 감지된 Python 확인: `stoke python list`
2. 필요한 Python 버전 설치, 또는
3. `stoke.toml`의 `python_version`을 가지고 있는 버전으로 변경

### `JDK X not found`

**원인**: 필요한 메이저 버전의 JDK가 없습니다.

**해결**:

1. 감지된 JDK 확인: `stoke java list`
2. 맞는 JDK 설치 (Adoptium 권장: [adoptium.net](https://adoptium.net))
3. 필요하다면 `JAVA_HOME` 설정
4. 또는 `stoke.toml`의 `java_version` 변경

### `No C compiler detected`

**원인**: gcc/clang이 `PATH`에 없습니다.

**해결**:

- **Windows**: MSYS2를 설치하고 `pacman -S mingw-w64-ucrt-x86_64-gcc` 실행. MSYS2 bin을 `PATH`에 추가.
- **macOS**: Xcode Command Line Tools 설치: `xcode-select --install`
- **Linux**: `sudo apt install build-essential` (Ubuntu/Debian) 또는 해당 배포판 명령어

## 런타임 에러

### `stoke run`이 조용히 실패함

**원인**: 타깃이 아직 빌드되지 않았습니다.

**해결**: 먼저 `stoke build`를 실행하세요.

### Python: `ModuleNotFoundError`

**원인**: import 경로가 올바르게 설정되지 않았습니다.

**해결**:

- 각 폴더에 `__init__.py`가 있는지 확인
- `src/` 기준 전체 경로 사용: `from utils.helpers import ...`
- [Python 소스 레이아웃](languages/python.md#source-layout) 확인

### Java: `Could not find or load main class`

**원인**: `stoke.toml`의 `main_class`가 실제 클래스 이름과 다릅니다.

**해결**: 완전한 형태의 클래스 이름이 일치하는지 확인하세요. 예:

```java
// src/main/java/com/example/Main.java
package com.example;
public class Main { ... }
```

```toml
main_class = "com.example.Main"    # 완전한 형태
```

## 캐시 / 락 관련 문제

### 외부 변경 후 빌드가 오래된 상태로 남음

**원인**: `sources` 밖의 무언가를 변경했고(예: 파일 이동, 환경변수 변경), 캐시가 오래된 상태입니다.

**해결**: 강제 재빌드:

```bash
stoke build --force
```

### 락 파일 불일치

**원인**: 락 파일이 더 이상 존재하지 않는 도구/의존성을 참조하고 있습니다.

**해결**: 완전 초기화:

```bash
stoke clean --all
stoke build
```

## vcpkg 관련 문제

### 라이브러리 설치가 끝나지 않음

**원인**: vcpkg는 소스에서 빌드합니다. Boost, Qt 같은 일부 라이브러리는 매우 오래 걸립니다.

**해결**: 기다려주세요. 처음 설치만 느리고, 이후 사용은 빠릅니다.

### 설치 후에도 `Library not found`

**원인**: vcpkg는 라이브러리를 설치했지만 stoke의 캐시가 오래된 상태입니다.

**해결**:

```bash
stoke build --force
```

### vcpkg가 손상됨

**원인**: 설치가 중단됐거나 시스템 문제.

**해결**:

```bash
stoke uninstall vcpkg
stoke install vcpkg
stoke build --force
```

## IDE 관련 문제

### VSCode가 잘못된 Python 인터프리터를 보여줌

**원인**: VSCode Python 확장이 venv 대신 전역 Python을 선택했습니다.

**해결**:

1. `.vscode/settings.json`을 다시 생성하도록 `stoke build` 실행
2. Ctrl+Shift+P → "Python: Select Interpreter" → `.stoke/python/<target>/venv/` 선택

### 일부 시스템에서 VSCode가 느려짐

**원인**: 파일 감시자 또는 확장 프로그램 과부하.

**해결**:

1. `.vscode/settings.json`이 `.stoke/`를 제외하고 있는지 확인
2. 하드웨어 가속 비활성화: settings.json → `"disable-hardware-acceleration": true`
3. 사용 안 하는 확장 비활성화
4. VSCode 재시작

관련 이슈: [일부 시스템에서 VSCode가 느려짐](https://github.com/dvdsvds/stoke/issues)

### C++ IntelliSense가 동작하지 않음

**원인**: `compile_commands.json`이 없거나 IDE가 못 찾고 있습니다.

**해결**:

1. `stoke build`를 실행해서 `compile_commands.json` 생성
2. 사용하는 확장이 그걸 읽는지 확인 (Microsoft C/C++ 확장은 `.vscode/c_cpp_properties.json`을 읽고, clangd는 `compile_commands.json`을 읽음)

## watch / hot-reload 관련 문제

### 변경이 감지되지 않음

**원인**: 파일이 `sources` glob 패턴 밖에 있습니다.

**해결**: `stoke.toml`의 `sources`가 모든 소스 파일을 포함하는지 확인하세요.

### hot-reload가 재시작되지 않음

**원인**: 프로세스가 깔끔하게 종료되지 않았거나 출력이 버퍼링되어 있습니다.

**해결**:

- 다시 시도 (일시적인 문제일 수 있음)
- Python/Java의 경우, 프로그램이 SIGTERM/SIGINT를 제대로 처리하는지 확인

## 그래도 해결이 안 된다면?

- 검색하거나 이슈 등록: [github.com/dvdsvds/stoke/issues](https://github.com/dvdsvds/stoke/issues)
- [FAQ](faq.md) 확인
