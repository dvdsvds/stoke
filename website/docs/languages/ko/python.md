# Python

stoke는 venv 생성, 의존성 설치, 문법 검사를 통해 Python 프로젝트를 관리합니다.

## `stoke.toml` 예시

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "python"
python_version = "3.12"
entry = "src/main.py"
sources = ["src/**/*.py"]

[targets.myapp.deps]
requests = "*"
flask = ">=2.0"
```

## Target 필드

| 필드 | 필수 | 설명 |
|-------|----------|-------------|
| `language` | 예 | `"python"` |
| `python_version` | 아니오 | 필요한 Python 버전 (예: `"3.12"`) |
| `entry` | 예 | `stoke run` 실행 스크립트 경로 |
| `sources` | 아니오 | 문법 검사할 파일 glob 패턴 |
| `deps` | 아니오 | pip 의존성 |

## Python 버전 감지

특정 버전을 요구하려면 `python_version` 설정:

```toml
python_version = "3.12"        # 3.12.x 요구
python_version = "3.12.5"      # 정확히 3.12.5 요구
```

stoke가 Python을 찾는 순서:

1. `PATH` (`python3.12`, `python3`, `python`)
2. `py` launcher (Windows)
3. 표준 설치 경로 (`%LOCALAPPDATA%\Programs\Python\...`, `/usr/bin/python3.X` 등)

일치하는 Python이 없으면 stoke는 감지된 Python 목록과 함께 종료합니다.

사용 가능한 Python 확인:

```bash
stoke python list
```

## venv

stoke는 프로젝트별 venv를 다음 위치에 생성:

    .stoke/python/{target}/venv/

venv는 Python 버전별. `python_version`을 변경하면 재생성됩니다.

## 의존성

`[targets.<name>.deps]`에 pip 의존성 선언:

```toml
[targets.myapp.deps]
requests = "*"                 # 모든 버전
flask = ">=2.0"                # 버전 제약
numpy = "==1.24.3"             # 정확한 버전
mypackage = "git+https://..."  # VCS
```

`stoke build` 시 stoke가 하는 일:

1. venv에 설치된 패키지 확인
2. 선언된 deps와 lock 파일과 비교
3. 필요한 경우 설치/업데이트
4. 잠긴 버전을 `.stoke/lock.toml`에 기록

이후 빌드는 venv가 lock 파일과 일치하면 설치 스킵.

## 소스 레이아웃

stoke는 표준 Python 규칙을 사용. 프로젝트 루트에서 import 가능하도록 구성:

    myapp/
    ├── stoke.toml
    └── src/
        ├── main.py
        ├── utils/
        │   ├── __init__.py
        │   └── helpers.py
        └── models/
            ├── __init__.py
            └── user.py

`main.py`:

```python
from utils.helpers import greet
from models.user import User
```

`src/` 기준으로 전체 경로 사용. 각 서브폴더에 `__init__.py` 필요.

stoke가 실행 시 `PYTHONPATH`를 자동 설정.

## 문법 검사

`stoke build`는 `sources`에 매칭되는 모든 파일에 `py_compile`을 실행:

    Building 'myapp' (python)...
    Using Python 3.12.12
    Checked 3 file(s), all passed
    Build complete: myapp

에러는 파일별로 표시:

    FAIL  src\main.py
    SyntaxError: unexpected EOF while parsing

## 실행

```bash
stoke run
```

venv의 Python과 올바른 `PYTHONPATH`로 `entry` 실행.

## IDE 통합

stoke가 `.vscode/settings.json` 자동 생성:

- Python 인터프리터를 venv로 설정
- import를 위한 추가 경로
- 파일 제외 (`.stoke/`, `__pycache__/`)

## 관련 문서

- [`stoke build`](../../commands/build.md)
- [`stoke run`](../../commands/run.md)
- [Lock file](../../configuration/lock-file.md)