# Rocket

Rocket 프로젝트 생성:

```bash
stoke init rocket
```

Rocket은 사용 편의성에 중점을 둔 Rust 웹 프레임워크입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── Cargo.toml
    └── src/
        └── main.rs           # Rocket 진입점

## 의존성

- `rocket` `0.5`

## 기본 설정

- **Port**: `8000` (Rocket 기본값)
- **Endpoints**:
  - `GET /` → `Hello from Rocket + stoke!`
  - `GET /hello/<name>` → `Hello, {name}!`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:8000/`

## 커스터마이징

- 포트 변경: `Rocket.toml`에 `[default] port = <port>` 추가하거나 `ROCKET_PORT` 환경변수 설정
- 라우트 추가: `#[get(...)]` 어노테이션 함수 추가 후 `routes![...]`에 등록
- state/fairing 추가: `rocket::build()`에 `.manage(...)` / `.attach(...)` 사용
