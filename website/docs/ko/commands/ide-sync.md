# stoke ide-sync

멀티 프로젝트 워크스페이스를 위한 IDE 설정을 생성합니다.

## 사용법

여러 stoke 프로젝트를 담고 있는 디렉토리에서 실행하세요:

```bash
stoke ide-sync
```

## 동작 방식

하위 디렉토리를 스캔해서 `stoke.toml` 파일을 찾고 다음을 생성합니다:

- `.vscode/settings.json` — VSCode 워크스페이스 설정
- `{workspace_name}.code-workspace` — VSCode 멀티 루트 워크스페이스 파일

## 예시

디렉토리 구조:
myworkspace/
├── frontend/
│   └── stoke.toml       # python
├── backend/
│   └── stoke.toml       # java
└── engine/
└── stoke.toml       # cpp

실행:
$ cd myworkspace
$ stoke ide-sync
Scanning for stoke projects under C:\Users...\myworkspace...
Found 3 project(s):
[python] frontend
[java] backend
[cpp] engine
Generated: C:\Users...\myworkspace.vscode\settings.json
Generated: C:\Users...\myworkspace\myworkspace.code-workspace
Open in VSCode: C:\Users...\myworkspace\myworkspace.code-workspace

VSCode에서 `.code-workspace` 파일을 열면 각 프로젝트에 맞는 언어 지원을 받으면서 모든 프로젝트를 함께 작업할 수 있습니다.

## 개별 프로젝트 IDE 파일

`stoke build`도 프로젝트별 IDE 파일(VSCode 설정, Eclipse `.classpath`, `pom.xml` 등)을 생성합니다. `ide-sync`와는 별개입니다.

- **stoke build** — 프로젝트별 IDE 파일 (단일 프로젝트)
- **stoke ide-sync** — 워크스페이스 단위 VSCode 설정 (여러 프로젝트)

## 관련 문서

- [IDE 연동](../advanced/ide-integration.md) — 자세히 알아보기
