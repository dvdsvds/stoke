# npm install이 스캐폴딩 중 조용히 실행 안 됨 (shell=True 버그)

- 날짜: 2026-09-17
- 심각도: critical
- 상태: fixed (stoke 자체 버그는 수정 완료, 외부 npm 버그는 경고로 완화)
- 재현: `stoke init express <project>` 후 `npm install prisma @prisma/client`

## 증상

`stoke init express`로 프로젝트를 만든 뒤 `npm install prisma @prisma/client`를 실행하면 아래 에러로 실패함:

```
npm ERR! Cannot read properties of null (reading 'edgesOut')
```

## 원인 1 (stoke 버그, 근본 원인) — 수정됨

`src/stoke/languages/javascript/frameworks/express.py` 등 npm/npx를 호출하는 8개 프레임워크 핸들러(express, fastify, nextjs, nuxt, hono, vite, sveltekit, nestjs) 전부에서 아래처럼 `subprocess.run`을 호출하고 있었음:

```python
subprocess.run(
    [npm_exe, "install"],
    cwd=str(project_path),
    capture_output=True,
    shell=True,
)
```

POSIX에서 `shell=True` + 리스트 인자 조합이면 `args[0]`만 셸 커맨드 문자열로 쓰이고 나머지(`"install"` 등)는 `$1`류 셸 위치 인자로 취급되어 커맨드 문자열이 참조하지 않으면 버려짐. 실제로는 `sh -c "<npm경로>" install` → npm이 서브커맨드 없이 실행되어 usage만 찍고 끝남. `capture_output=True`로 출력도 삼키고 리턴코드 체크도 없어서 **완전히 조용히 실패**.

결과: `stoke init express`로 만든 프로젝트에는 `package-lock.json`도 `node_modules`도 없는 상태로 남음. 이후 사용자가 처음 실행하는 `npm install`이 baseline lock 없이 전체 의존성 트리를 처음부터 구성해야 하는 상황이 되고, 이게 원인 2의 버그를 유발하는 트리거가 됨.

**수정**: 8개 파일 전부에서 `shell=True` 제거 (list 인자만으로 정상 동작), express/fastify는 `npm install` 실패 시 stderr를 출력하도록 리턴코드 체크 추가.

## 원인 2 (npm 자체 버그, 외부) — 경고로 완화

로그(`~/.npm/_logs/...debug-0.log`) 분석 결과:

```
1275 silly placeDep ROOT @effect/vitest@4.0.0-rc.112 OK for: @prisma/composer@0.20.0 want: 4.0.0-rc.112
1276 silly placeDep ROOT vitest@4.1.11 OK for: @effect/vitest@4.0.0-rc.112 want: >=4.1.0 <5.0.0
...
2985 verbose stack TypeError: Cannot read properties of null (reading 'edgesOut')
    at #loadPeerSet (.../@npmcli/arborist/lib/arborist/build-ideal-tree.js:1289:38)
    at async #loadPeerSet (...:1297:11)   ← 재귀 3단계 중첩
```

`prisma` → `@prisma/composer` → `@effect/vitest` → `vitest`로 이어지는 peer dependency 체인을 npm Arborist가 재귀적으로 `#loadPeerSet`을 로드하다가 null 노드를 참조해서 크래시. 환경은 `npm@10.9.9`, `node@v22.22.1`.

이건 [npm/cli#9787](https://github.com/npm/cli/issues/9787)에 등록된 알려진 버그이며 **npm 11.6.0에서 수정됨**. `npm < 10`이 원인이라는 초기 추측은 틀렸음(로그상 npm 10.9.9에서도 재현).

**대응**: stoke가 npm 자체를 고칠 수는 없으므로, 스캐폴딩 직전 `npm --version`을 확인해 `11.6.0` 미만이면 경고와 `npm install -g npm@latest` 권장 메시지를 출력하도록 `src/stoke/npm_check.py`를 추가하고 8개 핸들러에 연결함. 즉시 우회가 필요하면 `npm install --legacy-peer-deps` (단, peer dependency가 아예 설치 안 되어 런타임에 깨질 수 있는 임시방편).

## 변경 파일

- `src/stoke/languages/javascript/frameworks/express.py`
- `src/stoke/languages/javascript/frameworks/fastify.py`
- `src/stoke/languages/typescript/frameworks/nextjs.py`
- `src/stoke/languages/typescript/frameworks/nuxt.py`
- `src/stoke/languages/typescript/frameworks/hono.py`
- `src/stoke/languages/typescript/frameworks/vite.py`
- `src/stoke/languages/typescript/frameworks/sveltekit.py`
- `src/stoke/languages/typescript/frameworks/nestjs.py`
- `src/stoke/npm_check.py` (신규)
