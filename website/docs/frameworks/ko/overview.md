# 프레임워크 스캐폴딩

stoke는 인기 프레임워크의 실행 가능한 프로젝트를 명령어 하나로 생성합니다:

```bash
stoke init spring-boot
stoke init fastapi
stoke init flask
stoke init django
stoke init gin
stoke init echo
stoke init fiber
stoke init chi
```

각 명령어는 기본 설정 (프로젝트 이름, 언어 버전, 환경 타입 등)을 대화형으로 받고 샘플 코드와 함께 프로젝트 구조를 생성합니다.

## 지원 프레임워크

### Java

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init spring-boot` | Spring Boot (Spring Initializr 사용) |

### Python

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init fastapi` | FastAPI + uvicorn |
| `stoke init flask` | Flask + Jinja2 템플릿 |
| `stoke init django` | Django (프로젝트 + 앱 전체 구조) |

### Go

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init gin` | Gin — 인기 있는 고성능 HTTP 프레임워크 |
| `stoke init echo` | Echo — 미니멀, 고성능 |
| `stoke init fiber` | Fiber — Express 스타일 API |
| `stoke init chi` | Chi — 표준 라이브러리 기반 경량 라우터 |

## 생성되는 것

각 프레임워크별 페이지에서 생성 파일, 의존성, 기본 설정을 확인할 수 있습니다.

**Java:**
- [Spring Boot](spring-boot.md)

**Python:**
- [FastAPI](fastapi.md)
- [Flask](flask.md)
- [Django](django.md)

**Go:**
- [Gin](gin.md)
- [Echo](echo.md)
- [Fiber](fiber.md)
- [Chi](chi.md)

## 스캐폴딩 후

**Python 프레임워크**는 동일한 워크플로우:

```bash
stoke build     # venv/conda 환경 생성, 의존성 설치
stoke run       # 서버 시작
```

**Go 프레임워크**는 동일한 워크플로우:

```bash
stoke build     # go build
stoke run       # 서버 시작
```

**Spring Boot**는 스캐폴딩 후 Maven 사용 (stoke 사용 안 함):

```bash
cd myapp
mvnw spring-boot:run      # Linux/macOS
mvnw.cmd spring-boot:run  # Windows
```