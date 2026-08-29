# vcpkg 연동

stoke는 C/C++ 의존성 관리를 위해 [vcpkg](https://vcpkg.io)와 연동됩니다.

## 설치

vcpkg 설치:

```bash
stoke install vcpkg
```

stoke가 관리하는 위치에 vcpkg를 클론하고 부트스트랩합니다. 관리자 권한 필요 없습니다.

설치 확인:

```bash
stoke vcpkg version
```

제거:

```bash
stoke uninstall vcpkg
```

## 라이브러리 설치

두 가지 방법이 있습니다:

### 방법 1: 직접 설치 명령어

```bash
stoke vcpkg install fmt
stoke vcpkg install sqlite3
```

동작:

1. vcpkg를 통해 라이브러리를 다운로드하고 빌드
2. `stoke.toml`의 `[targets.<name>.deps]`에 추가

기본적으로 첫 번째 타깃에 추가됩니다. 타깃을 지정하려면:

```bash
stoke vcpkg install fmt --target=engine
```

### 방법 2: stoke.toml에 직접 추가

```toml
[targets.myapp.deps]
fmt = "*"
sqlite3 = "*"
```

그리고 실행:

```bash
stoke build
```

stoke는 선언됐지만 아직 없는 라이브러리를 자동으로 설치합니다.

## 라이브러리 제거

```bash
stoke vcpkg remove fmt
```

동작:

1. `stoke.toml`에서 제거
2. vcpkg의 remove 명령 실행

## 설치된 라이브러리 목록

```bash
stoke vcpkg list
```

또는 특정 타깃에 대해:

```bash
stoke vcpkg list --target=engine
```

## 특정 버전

특정 버전 설치:

```bash
stoke vcpkg install fmt --version=10.1.1
```

또는 `stoke.toml`에서:

```toml
[targets.myapp.deps]
fmt = "10.1.1"
```

사용 가능한 최신 버전은 `"*"`:

```toml
[targets.myapp.deps]
fmt = "*"
```

## stoke가 vcpkg를 사용하는 방식

빌드 시:

1. stoke가 `[targets.<name>.deps]`를 읽음
2. 각 라이브러리가 vcpkg로 설치됐는지 확인
3. vcpkg include 경로(예: `installed/x64-mingw-dynamic/include/`)를 컴파일 플래그에 추가
4. 링크 시점에 vcpkg 라이브러리 파일(`.a`, `.lib`, `.so` 등)을 링크

include 경로와 라이브러리 경로는 자동으로 처리됩니다. 코드에서는:

```cpp
#include <fmt/format.h>          // 추가 설정 없이 그냥 동작함
```

## 언어 호환성

일부 라이브러리는 C 전용, 일부는 C++ 전용입니다.

C 프로젝트:

```toml
[targets.myapp]
language = "c"

[targets.myapp.deps]
sqlite3 = "*"    # ✓ C 라이브러리
fmt = "*"        # ✗ C++ 전용, stoke가 에러를 냄
```

C++ 프로젝트:

```toml
[targets.myapp]
language = "cpp"

[targets.myapp.deps]
sqlite3 = "*"    # ✓ 동작함 (C 라이브러리는 C++에서도 사용 가능)
fmt = "*"        # ✓ C++ 라이브러리
```

stoke는 설치 전에 호환성을 검증합니다.

## 트리플렛

vcpkg는 **트리플렛**(아키텍처 + 플랫폼 + 링크 방식) 단위로 라이브러리를 빌드합니다.

자동 감지되는 기본값:

- Windows MinGW64: `x64-mingw-dynamic`
- Windows MSVC: `x64-windows`
- Linux x64: `x64-linux`
- macOS: `x64-osx` 또는 `arm64-osx`

의존성별로 `.stoke/lock.toml`에 저장됩니다.

## 문제 해결

### 설치 후 라이브러리를 못 찾음

`stoke build --force`로 캐시를 지우고 vcpkg를 다시 스캔해보세요.

### 설치 시간이 오래 걸림

Boost, Qt 같은 일부 라이브러리는 처음 설치할 때 한 시간까지 걸릴 수 있습니다. vcpkg가 소스에서 빌드하기 때문입니다. 이후 빌드는 빠릅니다.

### vcpkg 초기화

vcpkg가 손상됐다면:

```bash
stoke uninstall vcpkg
stoke install vcpkg
stoke build --force
```

## 관련 문서

- [`stoke.toml` 레퍼런스](../configuration/stoke-toml.md)
- [언어 / C/C++](../languages/cpp.md)
