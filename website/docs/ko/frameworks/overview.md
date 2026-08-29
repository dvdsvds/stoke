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

# Rust
stoke init actix-web
stoke init axum
stoke init rocket

# Kotlin
stoke init ktor
stoke init spring-boot-kotlin

# C#
stoke init aspnet-core

# Ruby
stoke init sinatra

# PHP
stoke init slim
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

### Rust

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init actix-web` | Actix-web — 성숙하고 고성능인 프레임워크 |
| `stoke init axum` | Axum — Tokio 팀이 만든 Tokio 기반 프레임워크 |
| `stoke init rocket` | Rocket — 사용 편의성 중심 프레임워크 |

### Kotlin

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init ktor` | Ktor — 경량, 코루틴 기반 프레임워크 |
| `stoke init spring-boot-kotlin` | Kotlin DSL + kotlin-spring 플러그인 사용 Spring Boot |

### C#

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init aspnet-core` | ASP.NET Core — minimal API 템플릿 |

### Ruby

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init sinatra` | Sinatra — 경량 웹 앱 DSL |

### PHP

| 명령어 | 프레임워크 |
| --- | --- |
| `stoke init slim` | Slim Framework — 경량 PSR-7 마이크로 프레임워크 |

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

**Rust:**
- [Actix-web](actix-web.md)
- [Axum](axum.md)
- [Rocket](rocket.md)

**Kotlin:**
- [Ktor](ktor.md)
- [Spring Boot (Kotlin)](spring-boot-kotlin.md)

**C#:**
- [ASP.NET Core](aspnet-core.md)

**Ruby:**
- [Sinatra](sinatra.md)

**PHP:**
- [Slim Framework](slim.md)

## 스캐폴딩 후

**Python, Go, JavaScript 프레임워크 (Express, Fastify), Rust, Ruby (Sinatra)**는 동일한 워크플로우:

```bash
stoke build
stoke run
```

**Spring Boot (Java 또는 Kotlin)**는 Maven 또는 Gradle 사용:

```bash
mvnw spring-boot:run       # Linux/macOS (Java, Maven)
mvnw.cmd spring-boot:run   # Windows (Java, Maven)
gradlew bootRun            # Linux/macOS (Kotlin, 또는 Java+Gradle)
gradlew.bat bootRun        # Windows
```

**Kotlin (Ktor)**과 **C# (ASP.NET Core)**는 위 컴파일 언어들과 동일하게 `stoke build` / `stoke run` 그대로 사용.

**PHP (Slim)**은 `stoke build` 이후 PHP 내장 개발 서버가 필요 — [Slim 프레임워크 페이지](slim.md) 참조.

**TypeScript 프레임워크 (Next.js, NestJS, Vite, Nuxt, SvelteKit, Hono)**는 각 프레임워크 명령어 사용:

```bash
npm run dev     # 개발
npm run build   # 프로덕션
```

stoke는 공식 스캐폴딩 도구 (`create-next-app`, `@nestjs/cli`, `nuxi`, `sv create` 등)를 호출하므로 최신 프로젝트 템플릿을 얻습니다.