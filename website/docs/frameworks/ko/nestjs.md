# NestJS

NestJS 프로젝트 생성:

```bash
stoke init nestjs
```

NestJS는 Angular 스타일 아키텍처 (모듈, 컨트롤러, 서비스)를 사용하는 TypeScript 백엔드 프레임워크입니다.

## 프롬프트

- **Project name**
- **Package manager**: npm / yarn / pnpm (NestJS CLI)

## 생성 파일

표준 NestJS 구조:

    myapp/
    ├── src/
    │   ├── main.ts
    │   ├── app.module.ts
    │   ├── app.controller.ts
    │   └── app.service.ts
    ├── test/
    ├── package.json
    ├── tsconfig.json
    └── nest-cli.json

## 의존성

표준 NestJS 의존성 (@nestjs/common, @nestjs/core, rxjs 등).

## 실행

stoke가 관리하지 않음 — NestJS 명령어 직접 사용:

```bash
cd myapp
npm run start:dev     # 개발 (핫 리로드)
npm run build         # 프로덕션 빌드
npm run start:prod    # 프로덕션 서버
```

브라우저: `http://localhost:3000/`

## 참고

- stoke는 NestJS 프로젝트를 빌드하거나 실행하지 않음
- 모듈 추가: `nest g module <name>`
- 컨트롤러 추가: `nest g controller <name>`
- 자세한 내용은 [NestJS 공식 문서](https://docs.nestjs.com) 참조