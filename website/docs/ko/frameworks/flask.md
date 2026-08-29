# Flask

Flask 프로젝트 생성:

```bash
stoke init flask
```

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름
- **Python version**: 감지된 파이썬 목록에서 선택 (`stoke init`이랑 동일)
- **Environment type**: venv 또는 conda

## 생성 파일

    myapp/
    ├── stoke.toml
    └── src/
        ├── main.py                        # Flask 진입점
        └── app/
            ├── __init__.py                # create_app()
            ├── routes.py                  # register_routes()
            ├── templates/
            │   └── index.html             # Jinja2 템플릿
            └── static/
                └── style.css              # 샘플 스타일시트

## 의존성

- `flask` (최신)

## 기본 설정

- **Host**: `0.0.0.0`
- **Port**: `5000`
- **Debug mode**: on
- **Endpoints**:
  - `GET /` → HTML 페이지 (`templates/index.html` 렌더링)
  - `GET /api/hello/<name>` → `{"message": "Hello, {name}!"}`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:5000/`

## 커스터마이징

- 포트 변경: `src/main.py`에서 `port=5000` 수정
- 라우트 추가: `src/app/routes.py` 편집
- 템플릿 추가: `src/app/templates/`에 `.html` 파일 생성
- 정적 파일 추가: `src/app/static/`에 CSS/JS/이미지 배치