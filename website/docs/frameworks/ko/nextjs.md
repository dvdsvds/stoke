# Next.js

Next.js 프로젝트 생성:

```bash
stoke init nextjs
```

Next.js는 SSR, SSG, 파일 기반 라우팅을 지원하는 React 풀스택 프레임워크입니다.

## 프롬프트

stoke는 `create-next-app`을 호출하며 다음을 물어봅니다:

- **Project name**
- **TypeScript?**
- **ESLint?**
- **Tailwind CSS?**
- **`src/` directory?**
- **App Router?**
- **Turbopack?**
- **Import alias?**

## 생성 파일

표준 Next.js 구조 (옵션에 따라 다름). `package.json`, `next.config.ts`, `app/` 또는 `pages/` 등.

## 의존성

표준 Next.js 의존성 (Next.js, React, TypeScript 선택 시).

## 실행

stoke가 관리하지 않음 — Next.js 명령어 직접 사용:

```bash
cd myapp
npm run dev         # 개발 서버
npm run build       # 프로덕션 빌드
npm start           # 프로덕션 서버
```

브라우저: `http://localhost:3000/`

## 참고

- stoke는 Next.js 프로젝트를 빌드하거나 실행하지 않음
- Next.js는 React 애플리케이션에 최적화된 자체 빌드 시스템 사용
- 자세한 내용은 [Next.js 공식 문서](https://nextjs.org/docs) 참조