# stoke add에서 패키지 여러 개 한 번에 받기

- 날짜: 2026-09-17
- 종류: feat
- 관련: [2026-09-17 [feat] stoke add runs npm install directly for JS-TS with bug bypass.md](<2026-09-17 [feat] stoke add runs npm install directly for JS-TS with bug bypass.md>)

## 배경

`stoke add`가 JS/TS에서 실제 `npm install`을 대신 실행해주게 된 뒤([관련 문서](<2026-09-17 [feat] stoke add runs npm install directly for JS-TS with bug bypass.md>)), `npm install prisma @prisma/client`처럼 패키지를 여러 개 한 번에 설치하는 흔한 케이스가 막혀 있었음 — 기존 `stoke add <package> [version]`은 패키지 하나만 받는 구조였어서 `stoke add prisma`, `stoke add @prisma/client`를 두 번 실행해야 했음.

## 변경

- `src/stoke/cli/__init__.py`: `add` 서브커맨드의 위치 인자를 `package` 단일 + `version` 선택에서 `packages` (`nargs="+"`) 하나로 통합.
- `src/stoke/cli/deps.py`: `cmd_add_dep(packages: list[str], target_name)`로 시그니처 변경.
  - **javascript/typescript**: 받은 패키지 리스트를 그대로 한 번의 `npm install pkg1 pkg2 ...` 호출에 넘김 (`resolve_npm_command()` 우회 로직 그대로 적용).
  - **python/java**: 기존 `stoke add <package> <version>` 문법 유지 -- `len(packages) == 1`이면 버전 없음, `== 2`면 `(package, version)`으로 해석, `> 2`면 에러. 두 언어 모두 애초에 패키지 하나만 지원했으므로 기존 동작과 100% 호환.

## 검증

argparse 파싱 확인:
```python
parse_args(['add', 'pytest'])                    # packages=['pytest']
parse_args(['add', 'pytest', '7.4.0'])            # packages=['pytest', '7.4.0']  (기존 방식 그대로)
parse_args(['add', 'prisma', '@prisma/client'])   # packages=['prisma', '@prisma/client']
```

scratchpad 테스트 프로젝트에서 `stoke add uuid dayjs` 실행 → 한 번의 npm install로 두 패키지 모두 `package.json`에 정상 추가됨 확인.

## 변경 파일

- `src/stoke/cli/__init__.py`
- `src/stoke/cli/deps.py`
