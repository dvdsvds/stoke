# Vite

Vite 프로젝트 생성:

```bash
stoke init vite
```

Vite는 빠른 프론트엔드 빌드 도구입니다. React, Vue, Svelte, 순수 JavaScript/TypeScript 지원.

## 프롬프트

stoke는 `npm create vite@latest`를 호출하며 다음을 물어봅니다:

- **Project name**
- **Framework**: React, Vue, Svelte, Solid, Preact, Lit, Qwik, Angular, vanilla
- **Variant**: JavaScript / TypeScript

## 생성 파일

표준 Vite 프로젝트 구조 (프레임워크 선택에 따라 다름).

## 의존성

프레임워크별 의존성 + Vite 빌드 도구.

## 실행

stoke가 관리하지 않음 — Vite 명령어 직접 사용:

```bash
cd myapp
npm install
npm run dev         # 개발 서버
npm run build       # 프로덕션 빌드
npm run preview     # 프로덕션 미리보기
```

브라우저: Vite가 표시하는 URL (보통 `http://localhost:5173/`)

## 참고

- stoke는 Vite 프로젝트를 빌드하거나 실행하지 않음
- Vite는 빠른 개발을 위한 HMR (Hot Module Replacement) 지원
- 자세한 내용은 [Vite 공식 문서](https://vitejs.dev) 참조