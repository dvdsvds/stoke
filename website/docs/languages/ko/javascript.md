# JavaScript

stoke는 Node.js 런타임을 사용해 JavaScript 프로젝트를 지원합니다.

## 요구사항

- Node.js 18 이상 (권장: 최신 LTS)
- 설치: `stoke install --language=nodejs --version=<version>`

## 설정

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "javascript"
entry = "src/main.js"
```

## 동작 방식

- `stoke build`는 `npm install` 실행 (`package.json`의 의존성 설치)
- `stoke run`은 `node <entry>` 실행
- 의존성은 `package.json`으로 관리

## 예시

새 JavaScript 프로젝트 생성:

```bash
mkdir myapp
cd myapp
stoke init
```

언어 메뉴에서 `JavaScript` 선택. stoke가:

- `stoke.toml` 생성
- `package.json` 생성
- Hello World가 있는 `src/main.js` 생성

그 다음:

```bash
stoke build
stoke run
```

## 프레임워크 스캐폴딩

```bash
stoke init express      # Express — 클래식 Node.js 웹 프레임워크
stoke init fastify      # Fastify — 빠르고 오버헤드 적음
```

자세한 내용은 [Frameworks](../../frameworks/ko/overview.md) 참조.

## 참고

- stoke는 `stoke.toml`의 `entry` 필드를 읽어 Node.js로 실행
- `node_modules/`는 `.gitignore`에 자동 추가
- 시스템 Node.js 사용 (또는 `stoke install`로 PATH에 추가된 것)