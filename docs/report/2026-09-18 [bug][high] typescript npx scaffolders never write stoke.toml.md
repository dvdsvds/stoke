# TypeScript npx 기반 스캐폴더 6개가 stoke.toml을 안 씀

- 날짜: 2026-09-18
- 심각도: high
- 상태: 발견됨, 미수정
- 발견 경위: "툴 없으면 자동 설치" 기능을 붙이다가 발견 — `stoke install`이 동작하려면 프로젝트 루트에 stoke.toml이 있어야 하는데, nextjs/nuxt/sveltekit/hono/vite/nestjs는 그게 아예 없었음.

## 문제

```
grep -rn "stoke.toml" src/stoke/languages/typescript/frameworks/*.py
```
→ 결과 없음.

`nextjs.py`, `nuxt.py`, `sveltekit.py`, `hono.py`, `vite.py`, `nestjs.py` 6개 전부 `create-next-app`/`nuxi`/`sv create`/`npm create hono`/`npm create vite`/`@nestjs/cli` 같은 써드파티 CLI로 프로젝트만 생성하고, **stoke.toml을 쓰는 코드가 하나도 없음**. 다른 모든 언어/프레임워크(express, fastify 포함— 같은 JS 계열인데도)는 전부 `_write_stoke_toml()` 헬퍼가 있는데 이 6개만 없음.

## 영향

`stoke init nextjs`(또는 nuxt/sveltekit/hono/vite/nestjs)로 프로젝트를 만들면 "project created" 성공 메시지는 뜨지만, 그 디렉토리에서 `stoke build`/`stoke run`/`stoke test`/`stoke add`를 실행하면 전부 "stoke.toml not found" 에러가 남 — **stoke가 관리할 수 없는 프로젝트가 생성됨**. 사실상 `stoke init`이라는 이름의 명령어가 stoke 프로젝트를 안 만드는 상태.

## 다음 단계 (미수정)

다른 프레임워크들처럼 각 파일에 `_write_stoke_toml(project_path, project_name)` 헬퍼를 추가하고, 스캐폴딩 완료 직후(CLI 도구 실행 성공 후) 호출하도록 고치면 됨. `entry`는 프레임워크마다 dev 서버 진입점이 달라서(`next dev`, `vite`, `nuxi dev` 등 대부분 커맨드 기반이라 `entry` 파일 지정이 애매함) — 기존 express/fastify처럼 `entry = "src/main.js"` 식이 아니라 `stoke build`/`run`이 이 6개에서 어떤 의미를 가져야 하는지부터 설계가 필요할 수 있음(예: `npm run dev`/`npm run build`를 그대로 감싸는 형태). 코드 수정 전에 설계 방향 확인 필요.
