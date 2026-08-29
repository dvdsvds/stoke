# stoke.toml 레퍼런스

`stoke.toml` 설정 파일의 전체 레퍼런스입니다.

## 파일 구조

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "cpp"
sources = ["src/**/*.cpp"]

[targets.myapp.deps]
fmt = "*"

[profiles.custom]
compile_flags = ["-O2"]
```

섹션:

- **`[project]`** — 프로젝트 전체 메타데이터
- **`[targets.<name>]`** — 빌드 타깃마다 하나씩
- **`[targets.<name>.deps]`** — 타깃의 의존성
- **`[profiles.<name>]`** — 빌드 프로파일 (C/C++ 전용)

## `[project]`

프로젝트 레벨 설정입니다.

```toml
[project]
name = "myapp"           # 필수. 프로젝트 이름.
version = "0.1.0"        # 선택. 프로젝트 버전.
lock_mode = "auto"       # 선택. 락 파일 동작.
jobs = 4                 # 선택. 기본 병렬 빌드 워커 수.
```

### 필드

| 필드 | 타입 | 설명 |
|-------|------|-------------|
| `name` | string | 프로젝트 이름 |
| `version` | string | semver 형식의 버전 |
| `lock_mode` | `"auto"` \| `"strict"` \| `"off"` | 락 파일 동작 (기본값: `"auto"`) |
| `jobs` | int | 빌드(C/C++)의 기본 병렬 워커 수 |

### `lock_mode` 값

- **`"auto"`**: 락 파일이 있으면 사용, 필요하면 갱신
- **`"strict"`**: 락 파일 필수, 버전이 안 맞으면 실패
- **`"off"`**: 락 파일을 사용하거나 쓰지 않음

## `[targets.<name>]`

빌드 타깃마다 하나씩. 여러 타깃 가능:

```toml
[targets.server]
language = "python"
entry = "src/server.py"

[targets.worker]
language = "python"
entry = "src/worker.py"
```

특정 타깃 빌드:

```bash
stoke build server
stoke run worker
```

타깃을 지정하지 않으면 파일의 첫 번째 타깃이 사용됩니다.

### 공통 필드

| 필드 | 필수 여부 | 설명 |
|-------|----------|-------------|
| `language` | 예 | `"python"`, `"java"`, `"c"`, `"cpp"` |
| `sources` | 경우에 따라 | 소스 파일 glob 패턴 |
| `pre_build` | 아니오 | 빌드 전에 순서대로 실행할 셸 명령어 |
| `post_build` | 아니오 | 빌드 후에 순서대로 실행할 셸 명령어 |
| `depends_on` | 아니오 | 이 타깃이 의존하는 타깃 이름 목록; 순서대로 먼저 빌드됨 |
| `build_system` | 아니오 | C/C++ 전용. `"cmake"`로 설정하면 stoke 자체 빌드 모델 대신 CMake에 위임 |
| `source_dir` | 아니오 | C/C++ + `build_system = "cmake"` 전용. `CMakeLists.txt`가 있는 폴더, 프로젝트 루트 기준 상대 경로 (기본값 `"."`) |

### Python 전용 필드

| 필드 | 설명 |
|-------|-------------|
| `python_version` | 필요한 Python 버전 |
| `entry` | 진입 스크립트 경로 |

### Java 전용 필드

| 필드 | 설명 |
|-------|-------------|
| `java_version` | 필요한 JDK 메이저 버전 |
| `main_class` | 완전한 형태의 메인 클래스 |

### C/C++ 전용 필드

| 필드 | 설명 |
|-------|-------------|
| `c_standard` | C 표준 (`"c11"`, `"c17"` 등) |
| `cpp_standard` | C++ 표준 (`"c++17"`, `"c++20"` 등) |
| `include_dirs` | 추가 include 디렉토리 |
| `jobs` | 프로젝트 레벨 `jobs` 오버라이드 |

## `[targets.<name>.deps]`

특정 타깃의 의존성. 언어마다 형식이 다릅니다.

### Python (pip)

```toml
[targets.myapp.deps]
requests = "*"
flask = ">=2.0"
numpy = "==1.24.3"
mypackage = "git+https://github.com/user/repo"
```

### Java (Maven)

```toml
[targets.myapp.deps]
"com.google.code.gson:gson" = "2.10.1"
"org.slf4j:slf4j-api" = "2.0.9"
```

키 형식: `"groupId:artifactId"`.

### C / C++ (vcpkg)

```toml
[targets.myapp.deps]
fmt = "*"
sqlite3 = "*"
```

버전은 vcpkg에 그대로 전달됩니다. `"*"`는 사용 가능한 최신 버전을 의미합니다.

## `[profiles.<name>]`

C/C++용 빌드 프로파일입니다.

```toml
[profiles.small]
compile_flags = ["-Os", "-flto"]
defines = { NDEBUG = 1 }

[profiles.clang]
compiler = "clang"
```

전체 레퍼런스는 [프로파일](profiles.md)을 참고하세요.

## 빌드 훅 { #build-hooks }

```toml
[targets.myapp]
language = "python"
pre_build = ["echo starting build"]
post_build = ["cp dist/myapp ./release/myapp"]
```

`stoke build`, `stoke build --all`, `stoke watch`, `stoke hot-reload` 모두에서 선언된 순서대로 셸을 통해 실행됩니다. `pre_build` 명령이 0이 아닌 값을 반환하면 빌드 자체를 건너뛰고, `post_build` 명령이 실패하면 빌드가 실패합니다.

> **보안 참고**: 이 명령어들은 `stoke.toml`에 적힌 문자열 그대로 사용자 권한으로 셸을 통해 실행됩니다. 신뢰하지 않는 저장소의 `stoke.toml`을 읽어보지 않고 `stoke build`를 실행하지 마세요.

## 타깃 의존성

```toml
[targets.backend]
language = "python"
depends_on = ["shared_lib"]
```

`stoke build backend`는 `shared_lib`을 자동으로 먼저 빌드합니다. `stoke build --all`은 의존성이 해결된 타깃들을 병렬로 빌드하고, 어떤 타깃의 `depends_on`이 끝날 때까지 기다렸다가 시작하며, 의존 대상이 실패한 타깃은 시도하지 않고 건너뜁니다. 알 수 없는 타깃 참조와 의존성 순환은 빌드가 시작되기 전, `stoke.toml`을 불러오는 시점에 거부됩니다.

## C/C++용 CMake { #cmake-for-cc }

이미 자체 `CMakeLists.txt`가 있는 C/C++ 타깃은 stoke 자체 컴파일 모델 대신 CMake에 위임할 수 있습니다:

```toml
[targets.engine]
language = "cpp"
build_system = "cmake"
source_dir = "."   # CMakeLists.txt가 있는 폴더, 프로젝트 루트 기준 상대 경로
```

`stoke build`/`run`/`watch`/`hot-reload`/`clean`은 stoke 자체 C/C++ 모델과 똑같이 동작하지만, 내부적으로는 `cmake -S <source_dir> -B <build_dir>`를 실행한 뒤 `cmake --build <build_dir>`를 실행하고, 생성된 실행 파일을 자동으로 찾습니다. `c_standard`/`cpp_standard`, `[profiles.*].compile_flags`/`defines`/`compiler`, `includes`는 이 경로에서는 무시됩니다 — `CMakeLists.txt`가 그걸 담당하며, 프로파일 이름만 `CMAKE_BUILD_TYPE`에 매핑됩니다 (`debug` → `Debug`, `release` → `Release`).

## 전체 예시

멀티 타깃 프로젝트:

```toml
[project]
name = "myservice"
version = "1.0.0"

# Python 백엔드
[targets.backend]
language = "python"
python_version = "3.12"
entry = "backend/main.py"
sources = ["backend/**/*.py"]

[targets.backend.deps]
fastapi = "*"
uvicorn = "*"

# C++ 엔진
[targets.engine]
language = "cpp"
sources = ["engine/src/**/*.cpp"]
cpp_standard = "c++20"
include_dirs = ["engine/include"]
jobs = 8

[targets.engine.deps]
fmt = "*"
spdlog = "*"

# 커스텀 프로파일
[profiles.native]
compile_flags = ["-O3", "-march=native"]
```

개별 타깃 빌드:

```bash
stoke build backend
stoke build engine --profile=native
```

## 관련 문서

- [프로파일](profiles.md)
- [락 파일](lock-file.md)
- 언어 가이드: [Python](../languages/python.md), [Java](../languages/java.md), [C/C++](../languages/cpp.md), [Go](../languages/go.md), [Rust](../languages/rust.md), [Kotlin](../languages/kotlin.md), [C#](../languages/csharp.md), [Ruby](../languages/ruby.md), [PHP](../languages/php.md), [JavaScript](../languages/javascript.md), [TypeScript](../languages/typescript.md)
