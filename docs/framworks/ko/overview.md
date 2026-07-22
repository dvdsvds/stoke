# 프레임워크 스캐폴딩

stoke는 인기 프레임워크의 실행 가능한 프로젝트를 명령어 하나로 생성합니다:

```bash
stoke init spring-boot
stoke init fastapi
stoke init flask
stoke init django
```

각 명령어는 기본 설정 (프로젝트 이름, Python/Java 버전, 환경 타입)을 대화형으로 받고 샘플 코드와 함께 프로젝트 구조를 생성합니다.

## 지원 프레임워크

| 명령어 | 언어 | 프레임워크 |
| --- | --- | --- |
| `stoke init spring-boot` | Java | Spring Boot (Spring Initializr 사용) |
| `stoke init fastapi` | Python | FastAPI + uvicorn |
| `stoke init flask` | Python | Flask + Jinja2 템플릿 |
| `stoke init django` | Python | Django (프로젝트 + 앱 전체 구조) |

## 생성되는 것

각 프레임워크별 페이지에서 생성 파일, 의존성, 기본 설정을 확인할 수 있습니다.

- [Spring Boot](spring-boot.md)
- [FastAPI](fastapi.md)
- [Flask](flask.md)
- [Django](django.md)

## 스캐폴딩 후

Python 프레임워크는 모두 동일한 워크플로우 사용:

```bash
stoke build     # venv/conda 환경 생성, 의존성 설치
stoke run       # 서버 시작
```

Spring Boot는 스캐폴딩 후 Maven 사용 (stoke 사용 안 함):

```bash
cd myapp
mvnw spring-boot:run      # Linux/macOS
mvnw.cmd spring-boot:run  # Windows
```