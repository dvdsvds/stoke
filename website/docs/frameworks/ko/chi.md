# Chi

Chi 프로젝트 생성:

```bash
stoke init chi
```

Chi는 `net/http` 기반의 Go 경량 라우터입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름
- **Go module name**: 예: `github.com/user/myapp` (기본값은 프로젝트 이름)

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── go.mod
    ├── main.go                    # Chi 진입점
    └── handlers/
        └── hello.go               # 샘플 핸들러

## 의존성

- `github.com/go-chi/chi/v5` (`go get`으로 설치)

## 기본 설정

- **Port**: `8080`
- **Middleware**: Logger (기본 포함)
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Chi + stoke!"}`
  - `GET /hello/{name}` → `{"message": "Hello, {name}!"}`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:8080/`

## 커스터마이징

- 포트 변경: `main.go`의 `http.ListenAndServe(":8080", r)` 수정
- 핸들러 추가: `handlers/`에 파일 생성, `main.go`에서 등록
- 미들웨어 추가: `main.go`의 `r.Use(...)` 사용

## 참고

Chi는 Go의 `net/http` 규칙을 따르므로 핸들러가 `func(w http.ResponseWriter, r *http.Request)` 형식입니다. 기존 Go HTTP 라이브러리와 미들웨어를 그대로 사용할 수 있습니다.