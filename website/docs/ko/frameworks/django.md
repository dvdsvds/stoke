# Django

Django 프로젝트 생성:

```bash
stoke init django
```

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름 (Django 프로젝트 패키지 이름으로도 사용)
- **Python version**: 감지된 파이썬 목록에서 선택 (`stoke init`이랑 동일)
- **Environment type**: venv 또는 conda

## 생성 파일

    myapp/
    ├── stoke.toml
    └── src/
        ├── main.py                        # stoke run 진입점 (manage.py runserver 호출)
        ├── manage.py                      # Django 관리 CLI
        ├── myapp/                         # 프로젝트 패키지
        │   ├── __init__.py
        │   ├── settings.py                # Django 설정
        │   ├── urls.py                    # 루트 URL 설정
        │   ├── wsgi.py
        │   └── asgi.py
        ├── hello/                         # 샘플 앱
        │   ├── __init__.py
        │   ├── apps.py
        │   ├── views.py
        │   ├── urls.py
        │   └── templates/
        │       └── hello/
        │           └── index.html         # 샘플 템플릿
        └── static/
            └── style.css                  # 샘플 스타일시트

## 의존성

- `django` (최신)

## 기본 설정

- **Host**: `127.0.0.1`
- **Port**: `8000`
- **DEBUG**: `True`
- **Database**: SQLite (`db.sqlite3`)
- **Endpoints**:
  - `GET /` → HTML 페이지 (`hello/templates/hello/index.html` 렌더링)
  - `GET /api/hello/<name>/` → `{"message": "Hello, {name}!"}`
  - `GET /admin/` → Django 관리자 페이지

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:8000/`

## 참고 사항

- `main.py`가 `manage.py runserver`를 subprocess로 호출하므로 `stoke run`이 개발 서버 시작
- 초기 마이그레이션 18개 대기 중 — `python src/manage.py migrate`로 적용
- 프로덕션에는 gunicorn, uvicorn 등 WSGI/ASGI 서버 사용 필요

## 커스터마이징

- 포트 변경: `src/main.py`의 `runserver`에 인자 전달
- 뷰 추가: `src/hello/views.py` 편집, `src/hello/urls.py`에 등록
- 앱 추가: `src/`에 새 폴더 생성, `settings.py`의 `INSTALLED_APPS`에 등록
- 템플릿 추가: 앱의 `templates/<앱이름>/`에 `.html` 파일 생성
- 정적 파일 추가: `src/static/`에 배치