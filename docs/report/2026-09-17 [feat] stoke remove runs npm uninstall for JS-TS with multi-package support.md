# stoke remove도 JS/TS에서 npm uninstall 실행 + 여러 패키지 지원

- 날짜: 2026-09-17
- 종류: feat
- 관련: [2026-09-17 [feat] stoke add runs npm install directly for JS-TS with bug bypass.md](<2026-09-17 [feat] stoke add runs npm install directly for JS-TS with bug bypass.md>), [2026-09-17 [feat] stoke add accepts multiple packages at once.md](<2026-09-17 [feat] stoke add accepts multiple packages at once.md>)

## 배경

`stoke add`를 JS/TS에서 실제 npm install을 대신 실행하고 여러 패키지를 한 번에 받도록 고친 뒤, `stoke remove`는 그대로 python/java 전용으로 남아있어서 대칭이 안 맞았음. JS/TS 타겟에서 `stoke remove <package>`를 실행하면 여전히 에러만 내고 끝났음.

## 변경

- `src/stoke/cli/__init__.py`: `remove` 서브커맨드의 `package` 단일 위치 인자를 `packages` (`nargs="+"`)로 변경 (add와 동일한 패턴).
- `src/stoke/cli/deps.py`:
  - `_npm_remove(config, packages)` 추가 — `resolve_npm_command()`로 npm 버그 우회 커맨드를 만든 뒤 `npm uninstall pkg1 pkg2 ...`를 한 번에 실행.
  - `cmd_remove_dep(packages: list[str], target_name)`로 시그니처 변경. javascript/typescript면 `_npm_remove`로 위임, 아니면 기존처럼 각 패키지에 대해 `stoke.toml`에서 제거 (여러 개면 루프 처리).

## 검증

scratchpad 테스트 프로젝트에서 `stoke remove uuid dayjs` 실행 → 한 번의 `npm uninstall`로 두 패키지 모두 `package.json`에서 정상 제거됨 확인.

## 변경 파일

- `src/stoke/cli/__init__.py`
- `src/stoke/cli/deps.py`
