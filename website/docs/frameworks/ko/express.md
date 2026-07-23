# Express

Express 프로젝트 생성:

```bash
stoke init express
```

Express는 Node.js의 클래식하고 미니멀한 웹 프레임워크입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── package.json
    └── src/
        ├── main.js                # Express 진입점
        └── routes/
            └── hello.js           # 샘플 라우터

## 의존성

- `express` (^4.19.0)

## 기본 설정

- **Port**: `3000`
- **Endpoints**:
  - `GET /` → `{"message": "Hello from Express + stoke!"}`
  - `GET /hello/:name` → `{"message": "Hello, {name}!"}`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:3000/`

## 커스터마이징

- 포트 변경: `src/main.js`의 `PORT` 수정
- 라우트 추가: `src/routes/`에 파일 생성, `main.js`에서 등록
- 미들웨어 추가: `main.js`의 `app.use(...)` 사용