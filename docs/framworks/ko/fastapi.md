# FastAPI

FastAPI 프로젝트 생성:

```bash
stoke init fastapi
```

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름
- **Python version**: 감지된 파이썬 목록에서 선택 (`stoke init`이랑 동일)
- **Environment type**: venv 또는 conda

## 생성 파일

    myapp/
    ├── stoke.toml
    └── src/
        ├── main.py                        # uvicorn 진입점
        └── app/
            ├── __init__.py                # create_app()
            └── routers/
                ├── __init__.py
                └── hello.py               # 샘플 라우터

## 의존성

- `fastapi` (최신)
- `uvicorn[standard]` (최신)

> **참고**: Python 3.13 이상에서 venv 사용 시 `uvicorn[standard]`가 `watchfiles` 빌드 실패로 설치 안 될 수 있음 (Rust 필요). conda 환경 사용을 권장.

## 기본 설정

- **Host**: `0.0.0.0`
- **Port**: `8000`
- **Endpoints**:
  - `GET /` → `{"message": "Hello from FastAPI + stoke!"}`
  - `GET /hello/{name}` → `{"message": "Hello, {name}!"}`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:8000/`

## 커스터마이징

- 포트 변경: `src/main.py`에서 `port=8000` 수정
- 라우터 추가: `src/app/routers/`에 파일 생성, `src/app/__init__.py`에서 등록