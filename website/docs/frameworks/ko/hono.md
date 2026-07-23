# Hono

Hono 프로젝트 생성:

```bash
stoke init hono
```

Hono는 엣지 컴퓨팅(Cloudflare Workers, Deno, Bun, Node.js)을 위한 가볍고 빠른 웹 프레임워크입니다.

## 프롬프트

stoke는 `npm create hono@latest`를 호출하며 다음을 물어봅니다:

- **Project name**
- **Template**: Cloudflare Workers, Cloudflare Pages, Deno, Bun, Node.js, Vercel, AWS Lambda 등
- **Package manager**

## 생성 파일

템플릿(엣지 플랫폼)에 따라 다름.

## 의존성

Hono 코어 + 플랫폼별 의존성.

## 실행

stoke가 관리하지 않음 — 플랫폼별 명령어 사용:

```bash
cd myapp
npm install
npm run dev
```

포트와 URL은 선택한 플랫폼에 따라 다름 (Cloudflare Workers는 보통 `http://localhost:8787/`).

## 참고

- stoke는 Hono 프로젝트를 빌드하거나 실행하지 않음
- Hono는 엣지 런타임에 최적화됨
- Node.js, Deno, Bun, Cloudflare Workers, Vercel, AWS Lambda 호환
- 자세한 내용은 [Hono 공식 문서](https://hono.dev) 참조