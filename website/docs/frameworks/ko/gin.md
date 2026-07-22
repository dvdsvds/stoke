# Gin

Gin 프로젝트 생성:

```bash
stoke init gin
```

Gin은 Go의 인기 있는 고성능 HTTP 웹 프레임워크입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름
- **Go module name**: 예: `github.com/user/myapp` (기본값은 프로젝트 이름)

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── go.mod
    ├── main.go                    # Gin 진입점
    └── handlers/
        └── hello.go               # 샘플 핸들러

## 의존성

- `github.com/gin-gonic/gin` (`go get`으로 설치)

## 기본 설정

- **Port**: `8080`
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Gin + stoke!"}`
  - `GET /hello/:name` → `{"message": "Hello, {name}!"}`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:8080/`

## 커스터마이징

- 포트 변경: `main.go`의 `r.Run(":8080")` 수정
- 핸들러 추가: `handlers/`에 파일 생성, `main.go`에서 등록
- 미들웨어 추가: `main.go`의 `r.Use(...)` 사용