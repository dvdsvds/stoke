# 자잘한 스캐폴딩 불일치 + 경미한 레이스 모음

- 날짜: 2026-09-17
- 심각도: medium/low 모음
- 상태: 대부분 수정됨 (axum 버전/Python "*" 의존성만 보류)

## Go: "go not found" 안내가 프레임워크마다 다름 (medium)

`gin.py:45-50`은 `go` 없을 때 `go mod init`/`go get` 수동 안내를 전부 출력하는데, `echo.py:46`, `fiber.py:46`, `chi.py:46`은 그냥 `"Warning: 'go' not found."` 한 줄만 찍고 끝남 — 사용자가 뭘 해야 할지 안내가 없음.

## JS/TS: npm 헬스체크 호출이 프레임워크마다 빠짐 (low/medium)

- `vite.py`, `hono.py`는 `warn_npm_health()`/`resolve_npm_command()` 관련 체크를 전혀 안 함 → 이번 세션에서 고친 게 맞는지 재확인 필요(아래 참고).
- `fastify.py`: `npm_exe`가 `None`일 때 **경고 메시지 자체가 안 나옴** — `express.py`는 "Warning: npm not found. Install manually."를 찍는데 fastify는 아무 말 없이 "Fastify project created"로 넘어감. `node_modules` 없이 끝나는데 사용자는 알 방법이 없음.

(참고: `resolve_npm_command`/`warn_npm_health` 자체는 이미 express/fastify/hono/vite/nextjs/nuxt/sveltekit/nestjs에 다 연결해뒀음 — 이 항목은 "npm 자체가 아예 없을 때"의 사용자 안내 메시지 누락에 대한 것으로, 별개 이슈.)

## Java: Maven JAR 다운로드가 원자적이지 않음 (medium, race condition)

`src/stoke/languages/java/maven.py:187-189`:

```python
dest_path.write_bytes(jar_data)
return dest_path
```

임시 파일에 쓰고 rename하는 방식이 아니라 바로 최종 경로에 씀. 같은 JAR을 두 `stoke build` 프로세스가 동시에 받으면(예: 두 타겟이 같은 의존성 공유, CI 매트릭스), 한쪽이 쓰는 도중 다른 쪽이 `dest_path.exists()` 체크를 통과해서 **아직 다 안 쓰인 파일**을 읽어갈 수 있음. SHA-1 체크로 다음 실행에 자연 치유되긴 하지만, 동시 실행 시 빌드가 비결정적으로 실패할 수 있음. 발생 확률은 낮음.

## Java Spring Boot: zip-slip 방어 없음 (low)

`spring_boot.py:139-140`: `zf.extractall(dest_dir)`를 엔트리별 경로 검증 없이 실행. `start.spring.io`에서 HTTPS로 받은 zip이라 익스플로잇 하려면 Initializr가 침해당하거나 MITM이 필요해서 위험도는 낮지만, 외부에서 받은 zip을 경로 검증 없이 푸는 건 방어적으로 고칠 만함.

## 기타 낮은 우선순위

- `axum.py:63`: `axum = "0.7"` 고정. axum 0.8은 라우트 문법이 `:name` → `{name}`로 바뀌어서, 생성된 `main.rs`의 `/hello/:name`이 0.7 기준으로는 맞지만 나중에 사용자가 버전만 0.8로 올리면 컴파일이 깨짐 — 버전과 문법이 암묵적으로 묶여있음.
- `express.py:72`: `express: "^4.19.0"` — Express 5가 나온 지 꽤 됐는데 계속 4.x만 스캐폴딩됨. 의도적인 선택인지 불명확.
- Python 프레임워크(fastapi/flask/django)들의 의존성이 전부 `"*"`(버전 제약 없음) — 최저 버전 하한이 없어서 나중에 호환성 깨지는 메이저가 나와도 그대로 설치됨.
- `slim.py:62`: `composer.json`의 `name`이 Composer 네이밍 규칙(소문자 `vendor/package`) 검증 없이 그대로 들어감 — 위의 "프로젝트 이름 미검증" 이슈와 동일 계열.

## 수정

- Go 3개 파일(echo/fiber/chi)에 gin과 동일한 `go mod init`/`go get` 수동 안내 블록 추가.
- `fastify.py`: `npm_exe`가 `None`일 때 express와 동일한 "Warning: npm not found. Install manually." 출력하도록 else 분기 추가. (vite.py/hono.py는 재확인 결과 이미 `resolve_npm_command()`를 통해 버전 체크가 적용돼 있어서 — 이 세션 앞부분에서 고쳤던 게 맞음 — 별도 수정 불필요.)
- `maven.py`: `dest_path.write_bytes()` → 임시 파일(`.tmp{pid}`)에 쓰고 `os.replace()`로 원자적 교체.
- zip-slip 방어는 위 ASP.NET Core/Spring Boot 문서에서 같이 처리.
- `slim.py`: `composer.json`의 `name`에 `.lower()` 추가.
- `express.py`: `package.json`의 `name`에 `.lower()` 추가 (npm 네이밍 규칙 대응).

## 보류 (미수정, 우선순위 낮음)

- `axum.py`의 `"0.7"` 버전 고정과 `express.py`의 Express 4.x 고정은 의도적 선택일 수 있어 버전을 바꾸지 않음 (axum 0.8로 올리려면 라우트 문법도 `{name}`으로 같이 바꿔야 해서 별도 작업 필요).
- Python 프레임워크(fastapi/flask/django)의 `"*"` 무제약 의존성은 그대로 둠 — 최저 버전 하한을 넣는 건 어떤 버전을 하한으로 잡을지 판단이 필요해서 별도 결정 사항으로 남김.
