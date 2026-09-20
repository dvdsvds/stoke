# npm 버그 우회를 전역 설치 대신 npx로

- 날짜: 2026-09-17
- 종류: feat (기존 npm 버전 경고 기능 개선)
- 관련: [2026-09-17 [critical][fixed] npm install silently skipped during JS-TS scaffolding.md](<2026-09-17 [critical][fixed] npm install silently skipped during JS-TS scaffolding.md>)

## 문제

이전에 추가한 `check_npm_health()`는 npm이 버그 있는 버전(< 11.6.0)이면 `npm install -g npm@latest`를 권장했음. 실제로 시도해보니 두 가지 문제가 있었음:

1. **EBADENGINE**: `npm@latest`(12.0.2)는 `engines.node: "^22.22.2 || ^24.15.0 || >=26.0.0"`을 요구하는데, 사용자 Node는 `v22.22.1`이라 미묘하게 버전이 낮아서 설치 자체가 막힘.
2. **EACCES**: 전역 npm 디렉토리(`/usr/local/lib/node_modules`)가 현재 사용자 소유가 아니라서 `sudo` 없인 전역 설치가 애초에 안 됨.
3. 근본적으로, **stoke는 언어/툴체인을 프로젝트별로 격리하는 게 원칙**인데(Python venv처럼), "전역 npm을 올려라"라고 안내하는 건 그 원칙과 맞지 않음.

## 해결

전역 npm을 아예 건드리지 않고, 문제되는 install 한 번만 `npx`로 고쳐진 버전의 npm을 그 자리에서 받아 써서 우회하도록 바꿈.

`src/stoke/npm_check.py`:

- `resolve_npm_command(npm_exe) -> list[str]`: 현재 npm이 정상이면 `[npm_exe]` 그대로 반환. 버그 있는 버전이면, npm 레지스트리에서 `npm@>=11.6.0`인 버전들의 `version`/`engines.node`를 `npm view ... --json`으로 조회하고, 직접 구현한 간이 semver 범위 매처(`^X.Y.Z`, `>=X.Y.Z`, `||` 지원)로 **현재 Node 버전과 실제로 호환되는 것 중 최신 버전**을 찾아 `["npx", "-y", "npm@<그 버전>"]`을 반환. 호환되는 버전이 없으면(Node 자체가 너무 오래됨) 경고만 띄우고 기존 `npm_exe` 사용.
- `warn_npm_health(npm_exe)`: create-next-app/nuxi/sv/nest 같이 stoke가 직접 npm을 호출하지 않고 npx로 써드파티 CLI만 실행하는 경우엔 커맨드를 바꿔칠 수 없으므로(그 CLI 내부에서 자체적으로 system npm을 호출함), 진단 경고만 출력.

## 적용 범위

- `resolve_npm_command()`로 실제 커맨드 스왑: express, fastify (`npm install`), hono, vite (`npm create ...`)
- `warn_npm_health()`로 경고만: nextjs, nuxt, sveltekit, nestjs (내부적으로 system npm을 호출하는 써드파티 CLI라 스왑 불가)

## 검증

로컬 npm 10.9.9(버그 있는 버전) 상태에서 `resolve_npm_command()` 호출 시 `npx npm@11.19.1`로 정확히 스왑됨을 확인. 실제로 그 커맨드로 `npm install`을 돌려서 `returncode: 0`, `node_modules`/`package-lock.json` 정상 생성 확인. 이후 전역 `npm --version`은 여전히 `10.9.9`로 그대로임 (sudo 불필요, 전역 상태 무변경).

## 변경 파일

- `src/stoke/npm_check.py`
- `src/stoke/languages/javascript/frameworks/express.py`
- `src/stoke/languages/javascript/frameworks/fastify.py`
- `src/stoke/languages/typescript/frameworks/hono.py`
- `src/stoke/languages/typescript/frameworks/vite.py`
- `src/stoke/languages/typescript/frameworks/nextjs.py`
- `src/stoke/languages/typescript/frameworks/nuxt.py`
- `src/stoke/languages/typescript/frameworks/sveltekit.py`
- `src/stoke/languages/typescript/frameworks/nestjs.py`
