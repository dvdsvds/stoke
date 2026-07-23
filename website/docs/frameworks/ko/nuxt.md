# Nuxt

Nuxt 프로젝트 생성:

```bash
stoke init nuxt
```

Nuxt는 SSR, SSG, 파일 기반 라우팅을 지원하는 Vue.js 풀스택 프레임워크입니다.

## 프롬프트

stoke는 `nuxi init`을 호출하며 다음을 물어봅니다:

- **Template**: minimal 등
- **Package manager**: npm / yarn / pnpm / bun
- **Initialize git repository?**

## 생성 파일

표준 Nuxt 구조:

    myapp/
    ├── app.vue
    ├── nuxt.config.ts
    ├── package.json
    └── (pages/, components/, etc.)

## 의존성

표준 Nuxt 의존성 (nuxt, vue).

## 실행

stoke가 관리하지 않음 — Nuxt 명령어 직접 사용:

```bash
cd myapp
npm install
npm run dev         # 개발 서버
npm run build       # 프로덕션 빌드
npm run preview     # 프로덕션 미리보기
```

브라우저: `http://localhost:3000/`

## 참고

- stoke는 Nuxt 프로젝트를 빌드하거나 실행하지 않음
- Nuxt는 Next.js와 비슷한 파일 기반 라우팅을 Vue에서 사용
- 자세한 내용은 [Nuxt 공식 문서](https://nuxt.com/docs) 참조