# 프레임워크 스캐폴딩

stoke는 인기 프레임워크의 실행 가능한 프로젝트를 명령어 하나로 생성합니다:

```bash
# Java
stoke init spring-boot

# Python
stoke init fastapi
stoke init flask
stoke init django

# Go
stoke init gin
stoke init echo
stoke init fiber
stoke init chi

# JavaScript
stoke init express
stoke init fastify

# TypeScript
stoke init nextjs
stoke init nestjs
stoke init vite
stoke init nuxt
stoke init sveltekit
stoke init hono
```

각 명령어는 기본 설정을 대화형으로 받고 샘플 코드와 함께 프로젝트 구조를 생성합니다.

## 지원 프레임워크

### Java

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init spring-boot` | Spring Boot (Spring Initializr 사용) |

### Python

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init fastapi` | FastAPI + uvicorn |
| `stoke init flask` | Flask + Jinja2 템플릿 |
| `stoke init django` | Django (프로젝트 + 앱 전체 구조) |

### Go

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init gin` | Gin — 인기 있는 고성능 HTTP 프레임워크 |
| `stoke init echo` | Echo — 미니멀, 고성능 |
| `stoke init fiber` | Fiber — Express 스타일 API |
| `stoke init chi` | Chi — 표준 라이브러리 기반 경량 라우터 |

### JavaScript

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init express` | Express — 클래식 Node.js 웹 프레임워크 |
| `stoke init fastify` | Fastify — 빠르고 오버헤드 적음 |

### TypeScript

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init nextjs` | Next.js — React 풀스택 |
| `stoke init nestjs` | NestJS — Angular 스타일 백엔드 |
| `stoke init vite` | Vite — 빠른 프론트엔드 빌드 도구 |
| `stoke init nuxt` | Nuxt — Vue 풀스택 |
| `stoke init sveltekit` | SvelteKit — Svelte 풀스택 |
| `stoke init hono` | Hono — 엣지 컴퓨팅 프레임워크 |

## 생성되는 것

각 프레임워크별 페이지에서 확인:

**Java:**
- [Spring Boot](spring-boot.md)

**Python:**
- [FastAPI](fastapi.md)
- [Flask](flask.md)
- [Django](django.md)

**Go:**
- [Gin](gin.md)
- [Echo](echo.md)
- [Fiber](fiber.md)
- [Chi](chi.md)

**JavaScript:**
- [Express](express.md)
- [Fastify](fastify.md)

**TypeScript:**
- [Next.js](nextjs.md)
- [NestJS](nestjs.md)
- [Vite](vite.md)
- [Nuxt](nuxt.md)
- [SvelteKit](sveltekit.md)
- [Hono](hono.md)

## 스캐폴딩 후

**Python, Go, JavaScript 프레임워크 (Express, Fastify)**는 동일한 워크플로우:

```bash
stoke build
stoke run
```

**Spring Boot**는 Maven 사용:

```bash
mvnw spring-boot:run      # Linux/macOS
mvnw.cmd spring-boot:run  # Windows
```

**TypeScript 프레임워크 (Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono)**는 각 프레임워크 명령어 사용:

```bash
npm run dev     # 개발
npm run build   # 프로덕션
```

stoke는 공식 스캐폴딩 도구 (`create-next-app`, `@nestjs/cli`, `nuxi`, `sv create` 등)를 호출하므로 최신 프로젝트 템플릿을 얻습니다.