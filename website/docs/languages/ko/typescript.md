# TypeScript

stoke는 tsx 런타임을 사용해 TypeScript 프로젝트를 지원합니다 (컴파일 단계 없음).

## 요구사항

- Node.js 18 이상
- 설치: `stoke install --language=nodejs --version=<version>`

## 설정

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "typescript"
entry = "src/main.ts"
```

## 동작 방식

- `stoke build`는 `npm install` 실행
- `stoke run`은 `tsx`로 entry 실행 (컴파일 + 실행 한 단계)
- 의존성은 `package.json`으로 관리
- 타입 검사는 `tsconfig.json`으로

## 예시

```bash
mkdir myapp
cd myapp
stoke init
```

`TypeScript` 선택. stoke가 생성:

- `stoke.toml`
- `tsx`, `typescript`, `@types/node`가 포함된 `package.json`
- `tsconfig.json`
- Hello World가 있는 `src/main.ts`

그 다음:

```bash
stoke build
stoke run
```

## 프레임워크 스캐폴딩

```bash
stoke init nextjs       # Next.js — React 풀스택
stoke init nestjs       # NestJS — Angular 스타일 백엔드
stoke init vite         # Vite — 빠른 프론트엔드 빌드 도구
stoke init nuxt         # Nuxt — Vue 풀스택
stoke init sveltekit    # SvelteKit — Svelte 풀스택
stoke init hono         # Hono — 엣지 컴퓨팅 프레임워크
```

자세한 내용은 [Frameworks](../../frameworks/ko/overview.md) 참조.

## 참고

- 런타임에 `tsx` 사용 (별도 컴파일 단계 없음)
- 프로덕션 빌드는 각 프레임워크의 빌드 명령어 사용 (예: `npm run build`)