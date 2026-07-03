# stoke

자동 venv 관리와 재현 가능한 빌드를 제공하는 다국어 빌드 툴이에요.

[← 메인 README로 돌아가기](../README.md) · [English](./README_en.md)

## 소개

**stoke**는 `stoke.toml` 하나로 가상환경, 의존성, 재현 가능한 빌드를 관리해요.

> 현재는 파이썬만 지원해요. Java, C/C++ 지원 예정이에요.

## 주요 기능

- **자동 venv 관리** — 타겟별로 가상환경을 만들고 재사용
- **파이썬 버전 선택** — 시스템에 설치된 파이썬을 감지해서 원하는 버전을 지정 가능
- **재현 가능한 빌드** — lock 파일(`stoke.lock`)로 팀원 전체가 같은 파이썬 버전, 같은 패키지 버전 사용
- **증분 빌드** — 안 바뀐 파일과 의존성은 mtime 기반 캐시로 skip
- **대화형 초기화** — `stoke init`으로 프로젝트 설정 자동 생성

## 설치

```bash
pip install stoke-build
```

파이썬 3.11 이상이 필요해요.

## 빠른 시작

```bash
# 1. 새 프로젝트 폴더 생성
mkdir myapp
cd myapp

# 2. 대화형으로 초기화
stoke init

# 3. src/ 폴더에 소스 파일 추가

# 4. 빌드
stoke build
```

## 명령어

| 명령어 | 설명 |
| --- | --- |
| `stoke init` | 대화형 프로젝트 초기화, `stoke.toml` 생성 |
| `stoke build [target]` | 타겟 빌드 (미지정 시 기본 타겟) |
| `stoke build --force` | 캐시 무시하고 전체 재빌드 |
| `stoke clean [target]` | 빌드 산출물 삭제 (venv, 캐시, `__pycache__`) |
| `stoke clean --all` | lock 파일 포함 완전 초기화 |
| `stoke python list` | 시스템에 설치된 파이썬 목록 |

## 설정 파일

`stoke.toml` 예시:

```toml
[project]
name = "myapp"
version = "0.1.0"
lock_mode = "commit"  # 또는 "local"

[targets.myapp]
language = "python"
python_version = "3.12"       # 선택사항, 생략 시 셸 기본 파이썬
sources = ["src/**/*.py"]
entry = "src/main.py"

[targets.myapp.deps]
requests = "2.31.0"
fastapi = ">=0.100.0"
```

### Lock 파일 모드

- **`commit`** — 프로젝트 루트에 `stoke.lock`, git에 커밋해서 팀 재현성 보장
- **`local`** — `.stoke/lock.toml`, gitignore돼서 개발자별 관리

### 의존성 버전 문법

pip specifier 문법을 그대로 따라요:

- `"2.31.0"` — 정확한 버전 (`==2.31.0`과 같음)
- `">=2.0.0"`, `"<3.0.0"`, `">=2.0,<3.0"` — 버전 범위
- `"*"` 또는 `""` — 아무 버전

## 동작 방식

`stoke build`를 실행하면 stoke는 이렇게 동작해요:

1. `stoke.toml`을 읽어서 타겟 찾기
2. 파이썬 버전 결정:
   - `stoke.lock`이 있으면 lock에 명시된 정확한 버전 사용
   - 없으면 `stoke.toml`의 `python_version`, 그것도 없으면 셸 기본 파이썬
3. `.stoke/venv/[target]/`에 가상환경 생성 (없을 때만)
4. 의존성 설치:
   - lock 파일이 있으면 정확한 버전으로 설치
   - 없으면 `stoke.toml` 명세로 설치하고 lock 파일 생성
   - 이미 최신 상태면 skip
5. `py_compile`로 소스 파일 문법 체크, 안 바뀐 파일은 skip (mtime 캐시)
6. 캐시를 `.stoke/cache.json`에 저장

## 로드맵

- **v0.1** (현재) — 파이썬 빌드 (venv, 의존성, 문법 체크, 증분 빌드)
- **v0.2** — Watch 모드 (`stoke watch`), hot-reload
- **v0.3** — Java 지원
- **v0.4** — C/C++ 지원 (`.so` 재로드 + 프로세스 재시작)
- **v0.5** — 패키지 레지스트리, `stoke install`, `stoke publish`

## 기여

버그 리포트와 PR 환영해요. 큰 변경은 먼저 이슈를 열어주세요.

## 라이선스

MIT