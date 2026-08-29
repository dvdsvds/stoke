# C / C++

stoke는 헤더 의존성 추적, 병렬 컴파일, 빌드 프로파일, vcpkg 통합을 통해 C/C++ 프로젝트를 관리합니다.

## `stoke.toml` 예시

C++ 프로젝트:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]
cpp_standard = "c++20"
```

C 프로젝트:

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "c"
sources = ["src/**/*.c"]
c_standard = "c11"

[targets.myapp.deps]
sqlite3 = "*"
```

## Target 필드

| 필드 | 필수 | 설명 |
|-------|----------|-------------|
| `language` | 예 | `"c"` 또는 `"cpp"` |
| `sources` | 예 | `.c`/`.cpp` 파일 glob 패턴 |
| `c_standard` | 아니오 | 예: `"c11"`, `"c17"` (C 전용) |
| `cpp_standard` | 아니오 | 예: `"c++17"`, `"c++20"`, `"c++23"` (C++ 전용) |
| `deps` | 아니오 | vcpkg 라이브러리 |
| `jobs` | 아니오 | 병렬 컴파일 워커 수 (기본: CPU 개수) |

## 컴파일러 감지

stoke가 사용하는 기본 컴파일러:

- **Linux**: `gcc` / `g++`
- **macOS**: `clang` / `clang++`
- **Windows**: MSYS2/MinGW의 `gcc` / `g++`

빌드 프로파일로 오버라이드:

```toml
[profiles.clang]
compiler = "clang"
```

```bash
stoke build --profile=clang
```

감지된 컴파일러 확인:

```bash
stoke c list       # C 컴파일러
stoke cpp list     # C++ 컴파일러
```

## 헤더 의존성

stoke는 gcc의 `-MMD` 플래그로 각 소스가 어떤 헤더를 include하는지 추적. 헤더가 변경되면 해당 헤더를 include하는 모든 파일이 재컴파일됩니다.

예: `include/utils.h` 변경 → `#include "utils.h"`를 (직간접적으로) include하는 모든 `.cpp` 파일이 재빌드됨.

헤더 의존성 파일 (`.d`)은 `.stoke/`의 오브젝트 파일 옆에 저장됩니다.

## Include 경로

stoke가 자동으로 추가:

- `src/` (프로젝트 루트 소스)
- `include/` (있으면)
- vcpkg include 경로 (설치된 의존성)
- `include_dirs`로 지정한 사용자 경로

추가 경로 지정:

```toml
[targets.myapp]
include_dirs = ["third_party/include"]
```

## Include 관례

`#include`에 명시적 경로 사용:

```cpp
#include "hardware/cpu.hpp"        // ✓ 좋음
#include "cpu.hpp"                 // ✗ 모호함
```

Python/Java/Rust/Go와 동일한 관례. import를 명확하게 하고 리팩토링을 안전하게 만듭니다.

## 병렬 컴파일

stoke는 기본적으로 파일을 병렬 컴파일 (워커 수 = CPU 코어).

오버라이드:

```toml
[targets.myapp]
jobs = 4
```

또는 `[project]`에서 전역 설정.

## 빌드 프로파일

기본 프로파일:

- **debug** — `-O0 -g -Wall`, `DEBUG` 정의
- **release** — `-O2`, `NDEBUG` 정의

커스텀 프로파일:

```toml
[profiles.small]
compile_flags = ["-Os", "-flto"]
defines = { NDEBUG = 1 }

[profiles.native]
compile_flags = ["-O3", "-march=native"]

[profiles.clang]
compiler = "clang"
compile_flags = ["-O2"]
```

빌드:

```bash
stoke build --profile=small
```

자세한 내용은 [Profiles](../../configuration/profiles.md) 참조.

## 의존성 (vcpkg)

C/C++ 라이브러리는 [vcpkg](https://vcpkg.io)로 관리:

```toml
[targets.myapp.deps]
sqlite3 = "*"
fmt = "*"
```

먼저 vcpkg 설치:

```bash
stoke install vcpkg
```

라이브러리 설치:

```bash
stoke vcpkg install sqlite3
stoke vcpkg install fmt
```

또는 `stoke.toml`에 수동으로 추가 후 `stoke build` 실행 — stoke가 자동 설치.

자세한 내용은 [vcpkg 가이드](../../advanced/vcpkg.md) 참조.

## IDE 통합

`stoke build`가 자동 생성:

- `compile_commands.json` — clangd, VSCode C/C++ 확장 등
- `.vscode/c_cpp_properties.json` — Microsoft C/C++ 확장
- `.vscode/settings.json` — 파일 제외, 확장 설정

VSCode에서 C/C++ 확장으로 프로젝트 열면 IntelliSense가 바로 동작.

## 출력 구조

    .stoke/
    ├── cpp/
    │   └── myapp/
    │       ├── debug/
    │       │   ├── objects/       # .o 파일
    │       │   ├── myapp.d.*      # 헤더 의존성 파일
    │       │   └── myapp.exe
    │       └── release/
    │           ├── objects/
    │           └── myapp.exe

## 관련 문서

- [`stoke build`](../../commands/build.md)
- [Profiles](../../configuration/profiles.md)
- [vcpkg](../../advanced/vcpkg.md)