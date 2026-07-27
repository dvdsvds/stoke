# Axum

Axum 프로젝트 생성:

```bash
stoke init axum
```

Axum은 Tokio 팀이 만든 Tokio 기반 웹 프레임워크입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── Cargo.toml
    └── src/
        └── main.rs           # Axum 진입점

## 의존성

- `axum` `0.7`
- `tokio` `1` (`full` 기능 포함)

## 기본 설정

- **Port**: `8080`
- **Endpoints**:
  - `GET /` → `Hello from Axum + stoke!`
  - `GET /hello/:name` → `Hello, {name}!`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:8080/`

## 커스터마이징

- 포트 변경: `src/main.rs`의 `TcpListener::bind("127.0.0.1:8080")` 수정
- 라우트 추가: `Router`에 `.route("/path", get(handler))` 호출 추가
- 미들웨어 추가: `Router`에 `.layer(...)` 사용
