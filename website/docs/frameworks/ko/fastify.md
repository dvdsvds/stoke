# Fastify

Fastify 프로젝트 생성:

```bash
stoke init fastify
```

Fastify는 Node.js의 빠르고 오버헤드가 적은 웹 프레임워크입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── package.json
    └── src/
        ├── main.js                # Fastify 진입점
        └── routes/
            └── hello.js           # 샘플 라우터

## 의존성

- `fastify` (^5.0.0)

## 기본 설정

- **Port**: `3000`
- **Host**: `0.0.0.0`
- **Logger**: 활성화
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Fastify + stoke!"}`
  - `GET /hello/:name` → `{"message": "Hello, {name}!"}`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:3000/`

## 참고

- ES 모듈 사용 (`"type": "module"` in package.json)
- Fastify는 Express보다 일반적으로 빠르고 JSON 스키마 검증 내장

## 커스터마이징

- 포트 변경: `src/main.js`의 `port: 3000` 수정
- 라우트 추가: `src/routes/`에 파일 생성, `main.js`에서 등록
- 플러그인 추가: `main.js`의 `fastify.register(...)` 사용