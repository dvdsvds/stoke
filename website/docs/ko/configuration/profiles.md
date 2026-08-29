# 빌드 프로파일

빌드 프로파일을 쓰면 코드를 수정하지 않고도 서로 다른 빌드 설정을 전환할 수 있습니다. 현재는 **C, C++**에서만 지원됩니다.

## 내장 프로파일

stoke는 기본 프로파일 두 개를 제공합니다:

### debug

```toml
compile_flags = ["-O0", "-g", "-Wall"]
defines = { DEBUG = 1 }
```

`stoke build`를 실행할 때 기본값입니다. 개발에 적합합니다:

- 최적화 없음 (`-O0`)
- 전체 디버그 정보 (`-g`)
- 모든 경고 활성화 (`-Wall`)
- 조건부 컴파일을 위한 `DEBUG` 정의

### release

```toml
compile_flags = ["-O2"]
defines = { NDEBUG = 1 }
```

`--release`와 함께 사용:

- 최적화 (`-O2`)
- `NDEBUG` 정의 (`assert()` 등 비활성화)

## 프로파일 사용하기

```bash
stoke build                     # debug (기본값)
stoke build --debug             # debug (명시적)
stoke build --release           # release
stoke build --profile=    # 커스텀 프로파일
```

`stoke run`, `stoke watch`도 마찬가지:

```bash
stoke run --release
stoke watch --profile=custom
stoke hot-reload --release
```

## 커스텀 프로파일

`stoke.toml`에서 커스텀 프로파일을 정의하세요:

```toml
[profiles.<name>]
compile_flags = [...]     # 추가 컴파일러 플래그
defines = { KEY = value } # 전처리기 define
compiler = "..."          # 선택사항: 컴파일러 오버라이드
```

### 예시: 크기 최적화

```toml
[profiles.small]
compile_flags = ["-Os", "-flto", "-s"]
defines = { NDEBUG = 1 }
```

```bash
stoke build --profile=small
```

### 예시: 네이티브 최적화

```toml
[profiles.native]
compile_flags = ["-O3", "-march=native"]
defines = { NDEBUG = 1, NATIVE_BUILD = 1 }
```

### 예시: clang 오버라이드

```toml
[profiles.clang]
compiler = "clang"
compile_flags = ["-O2", "-Wall", "-Wextra"]
```

`compiler` 필드는 이 프로파일의 기본 컴파일러를 오버라이드합니다. 값: `"gcc"` 또는 `"clang"`.

## 출력 디렉토리

각 프로파일은 자기만의 디렉토리에 빌드됩니다:
.stoke/
└── cpp/
└── myapp/
├── debug/
│   └── myapp.exe
├── release/
│   └── myapp.exe
└── small/
└── myapp.exe

다른 프로파일을 다시 빌드해도 서로 영향을 주지 않습니다. 여러 빌드를 동시에 유지할 수 있습니다.

## 충돌

플래그 스타일을 섞어 쓸 수는 없습니다:

```bash
stoke build --debug --release           # 에러: 함께 쓸 수 없음
stoke build --release --profile=small   # 에러: 함께 쓸 수 없음
```

## Python/Java에는 적용 안 됨

프로파일은 C/C++에만 적용됩니다. Python과 Java 빌드는 프로파일 플래그를 무시하지만, 프로파일 기반 출력 디렉토리는 그대로 사용합니다:
.stoke/
├── python/
│   └── myapp/
│       └── venv/            # 프로파일과 무관하게 동일한 venv
└── java/
└── myapp/
└── debug/           # 기본 프로파일 디렉토리
└── classes/

## 사용 가능한 필드

프로파일 필드:

| 필드 | 타입 | 설명 |
|-------|------|-------------|
| `compile_flags` | list[string] | 컴파일러에 전달할 추가 플래그 |
| `defines` | table | 전처리기 `-D` define |
| `compiler` | string | 컴파일러 오버라이드 (`"gcc"` 또는 `"clang"`) |

## 관련 문서

- [`stoke build`](../commands/build.md)
- [언어 / C/C++](../languages/cpp.md)
