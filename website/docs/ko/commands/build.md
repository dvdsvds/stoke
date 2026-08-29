# stoke build

타깃을 빌드합니다.

## 사용법

```bash
stoke build [target] [options]
```

`target`을 생략하면 `stoke.toml`의 첫 번째 타깃이 사용됩니다.

## 옵션

| 옵션 | 설명 |
|--------|-------------|
| `--force` | 캐시를 무시하고 전체 재빌드 |
| `--debug` | debug 프로파일로 빌드 (기본값) |
| `--release` | release 프로파일로 빌드 |
| `--profile <name>` | `stoke.toml`의 커스텀 프로파일로 빌드 |
| `-v`, `--verbose` | 자세한 빌드 출력 표시 |

## 예시

### 기본 빌드

```bash
stoke build
```

기본 타깃을 debug 프로파일로 빌드합니다.

### 타깃 지정

```bash
stoke build myapp
```

`myapp` 타깃을 빌드합니다.

### Release 빌드

```bash
stoke build --release
```

최적화된 빌드입니다 (C/C++는 `-O2`, `NDEBUG` 정의).

### 커스텀 프로파일

```toml
# stoke.toml
[profiles.small]
compile_flags = ["-Os", "-flto"]
defines = { NDEBUG = 1 }
```

```bash
stoke build --profile=small
```

### 강제 재빌드

```bash
stoke build --force
```

캐시를 무시하고 전부 재컴파일합니다. 산출물이 오래됐다고 의심될 때 유용합니다.

### 자세한 출력

```bash
stoke build -v
```

컴파일러 경로, 파일별 컴파일 상태, 세부 단계를 보여줍니다.

## 출력 구조 { #output-structure }

빌드 산출물은 언어, 타깃, 프로파일별로 정리됩니다:
.stoke/
├── {language}/
│   └── {target}/
│       └── {profile}/
│           ├── objects/         # C/C++ .o 파일
│           ├── classes/         # Java .class 파일
│           └── {target}.exe     # 최종 실행 파일
├── cache.json                   # 증분 빌드 캐시
└── lock.toml                    # 고정된 버전

C 프로젝트 예시:
.stoke/
├── c/
│   └── myapp/
│       ├── debug/
│       │   ├── objects/
│       │   └── myapp.exe
│       └── release/
│           ├── objects/
│           └── myapp.exe
├── cache.json
└── lock.toml

## 증분 컴파일

stoke는 파일 수정과 헤더 의존성을 추적합니다. 변경된 파일만 재컴파일됩니다.

C/C++의 경우 gcc의 `-MMD` 플래그로 헤더 의존성을 추적합니다. `header.h`가 변경되면 (직접 또는 간접적으로) `#include "header.h"`하는 모든 파일이 재컴파일됩니다.

캐시를 무시하려면 `--force`를 사용하세요.

## 빌드 프로파일

기본 프로파일:

- **debug** — `-O0 -g -Wall`, `DEBUG` 정의 (C/C++만 해당)
- **release** — `-O2`, `NDEBUG` 정의 (C/C++만 해당)

참고: 프로파일은 C/C++ 빌드에만 영향을 줍니다. Python과 Java는 프로파일을 무시합니다.

커스텀 프로파일은 `stoke.toml`에서 정의합니다:

```toml
[profiles.myprofile]
compile_flags = ["-O3", "-march=native"]
defines = { MYFLAG = 1 }
compiler = "clang"  # 선택사항: 컴파일러 오버라이드
```

자세한 내용은 [프로파일](../configuration/profiles.md)을 참고하세요.

## 관련 문서

- [`stoke run`](run.md) — 빌드된 타깃 실행
- [`stoke watch`](watch.md) — 변경 시 자동 재빌드
- [`stoke clean`](clean.md) — 빌드 산출물 제거
- [프로파일](../configuration/profiles.md) — 프로파일 시스템 레퍼런스
