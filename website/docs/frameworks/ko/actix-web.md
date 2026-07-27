# Actix-web

Actix-web 프로젝트 생성:

```bash
stoke init actix-web
```

Actix-web은 성숙하고 고성능인 Rust 웹 프레임워크입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── Cargo.toml
    └── src/
        └── main.rs           # Actix-web 진입점

## 의존성

- `actix-web` `4` (`Cargo.toml`에 선언, 빌드 시 Cargo가 다운로드)

## 기본 설정

- **Port**: `8080`
- **Endpoints**:
  - `GET /` → `Hello from Actix-web + stoke!`
  - `GET /hello/{name}` → `Hello, {name}!`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:8080/`

## 커스터마이징

- 포트 변경: `src/main.rs`의 `.bind(("127.0.0.1", 8080))` 수정
- 라우트 추가: `#[get(...)]` / `#[post(...)]` 어노테이션 함수 추가 후 `.service(...)`로 등록
- 미들웨어 추가: `App`에 `.wrap(...)` 사용
