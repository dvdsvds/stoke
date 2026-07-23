# SvelteKit

SvelteKit 프로젝트 생성:

```bash
stoke init sveltekit
```

SvelteKit은 SSR, SSG, 파일 기반 라우팅을 지원하는 Svelte 풀스택 프레임워크입니다.

## 프롬프트

stoke는 `npx sv create`를 호출하며 다음을 물어봅니다:

- **Template**: SvelteKit minimal, demo app, library
- **TypeScript?**
- **Additional tools**: ESLint, Prettier, Playwright, Vitest

## 생성 파일

표준 SvelteKit 구조:

    myapp/
    ├── src/
    │   ├── routes/
    │   └── app.html
    ├── static/
    ├── svelte.config.js
    ├── vite.config.ts
    └── package.json

## 의존성

표준 SvelteKit 의존성.

## 실행

stoke가 관리하지 않음 — SvelteKit 명령어 직접 사용:

```bash
cd myapp
npm install
npm run dev         # 개발 서버
npm run build       # 프로덕션 빌드
npm run preview     # 프로덕션 미리보기
```

브라우저: `http://localhost:5173/`

## 참고

- stoke는 SvelteKit 프로젝트를 빌드하거나 실행하지 않음
- SvelteKit은 빌드 시 Svelte 컴포넌트를 컴파일
- 자세한 내용은 [SvelteKit 공식 문서](https://svelte.dev/docs/kit) 참조