# IDE 연동

stoke는 `stoke build` 중에 IDE 설정 파일을 자동으로 생성합니다. IDE에서 프로젝트를 열기만 하면 바로 동작합니다.

## 지원 IDE

| IDE | Python | Java | C/C++ |
|-----|--------|------|-------|
| VSCode | ✓ | ✓ | ✓ |
| Eclipse | | ✓ | |
| IntelliJ / JetBrains | | ✓ (Maven 경유) | |
| clangd 기반 | | | ✓ |

## VSCode

### 생성되는 파일

프로젝트별 (프로젝트 루트에):

- `.vscode/settings.json`

C/C++의 경우:
- `.vscode/c_cpp_properties.json` (Microsoft C/C++ 확장)
- `compile_commands.json` (clangd, Native Debug)

Java의 경우:
- `.classpath` (Eclipse 형식, VSCode Java 확장에서 사용)
- `.project` (Eclipse 형식)
- `pom.xml` (Maven 형식)

### 설정 내용

`settings.json`에 포함되는 것:

- **Python**: 인터프리터 경로, 추가 경로, 제외 항목
- **Java**: 소스 경로, 참조 JAR
- **C/C++**: include 경로, define, 컴파일러 경로

에디터 렉을 줄이기 위해 `.stoke/`는 파일 감시에서도 제외됩니다.

### 확장 프로그램

추천 VSCode 확장:

- **Python** — Microsoft Python 확장
- **Java** — Extension Pack for Java
- **C/C++** — Microsoft C/C++ 확장 또는 clangd

## Eclipse (Java)

기존 Eclipse 프로젝트로 임포트:

1. File → Import → General → Existing Projects into Workspace
2. 프로젝트 폴더 선택

Eclipse가 `.classpath`와 `.project`를 읽습니다.

## IntelliJ / JetBrains (Java)

Maven 프로젝트로 임포트:

1. File → Open → 프로젝트 폴더 또는 `pom.xml` 선택
2. IntelliJ가 `pom.xml`을 읽습니다

## clangd (C/C++)

프로젝트 루트의 `compile_commands.json`은 clangd 기반 도구들의 표준입니다:

- clangd LSP 서버
- CLion (clangd 경유)
- Neovim + clangd
- Emacs + clangd
- clangd를 지원하는 모든 에디터

추가 설정 필요 없이 프로젝트를 열기만 하면 됩니다.

## 멀티 프로젝트 워크스페이스

여러 stoke 프로젝트가 있는 저장소의 경우:
myworkspace/
├── frontend/         # python
│   └── stoke.toml
├── backend/          # java
│   └── stoke.toml
└── engine/           # cpp
└── stoke.toml

루트에서 실행:

```bash
stoke ide-sync
```

생성되는 것:

- `.vscode/settings.json` — 워크스페이스 레벨 설정
- `myworkspace.code-workspace` — 멀티 루트 VSCode 워크스페이스

`.code-workspace` 파일을 열면 모든 프로젝트를 함께 작업할 수 있습니다.

자세한 내용은 [`stoke ide-sync`](../commands/ide-sync.md)를 참고하세요.

## IDE 파일 재생성

IDE 파일은 `stoke build`마다 다시 생성됩니다. 동기화가 안 맞는 경우(예: 의존성 변경 후) 그냥 다시 빌드하세요:

```bash
stoke build
```

또는 강제로:

```bash
stoke build --force
```

## 수동으로 수정하지 마세요

IDE 파일은 재생성되기 때문에, 수동으로 수정해도 다음 빌드 때 덮어써집니다. 대신 `stoke.toml`을 통해 설정하세요.

`stoke.toml`에 추가 include 경로 넣기:

```toml
[targets.myapp]
include_dirs = ["third_party/include"]
```

## 관련 문서

- [`stoke ide-sync`](../commands/ide-sync.md)
- [`stoke build`](../commands/build.md)
