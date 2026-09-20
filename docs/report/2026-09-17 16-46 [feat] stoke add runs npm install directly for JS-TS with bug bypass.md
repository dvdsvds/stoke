# stoke add가 JS/TS에서 npm install을 직접 실행하도록 개선

- 날짜: 2026-09-17
- 종류: feat
- 관련: [2026-09-17 [feat] npm auto-resolve via npx instead of global npm upgrade.md](<2026-09-17 [feat] npm auto-resolve via npx instead of global npm upgrade.md>)

## 변경 전

`stoke add <package>`는 `stoke.toml`의 `[targets.X.deps]`가 실제 의존성 매니페스트인 언어(python/java)에서만 동작했음. javascript/typescript 타겟에서 실행하면 아래처럼 에러만 내고 끝났음:

```
Error: 'stoke add' doesn't apply to 'javascript' targets.
  stoke.toml isn't the dependency manifest here — use: npm install <package>
```

이 안내대로 사용자가 직접 `npm install <package>`를 돌리면, npm이 버그 있는 버전(< 11.6.0)일 때 `edgesOut` 크래시를 그대로 맞음 — stoke가 만들어둔 `resolve_npm_command()` 우회 로직([2026-09-17 [feat] npm auto-resolve...](<2026-09-17 [feat] npm auto-resolve via npx instead of global npm upgrade.md>))의 혜택을 못 받음.

## 변경 후

`src/stoke/cli/deps.py`의 `cmd_add_dep()`에서 `target.language`가 `javascript`/`typescript`면 에러를 내는 대신 `_npm_add()`를 호출해서 실제로 `npm install <package>[@version]`을 실행함. 이때 `stoke.npm_check.resolve_npm_command()`를 거치므로, 버그 있는 npm이 감지되면 자동으로 `npx npm@<호환버전>`으로 우회 실행됨.

```python
def _npm_add(config, package: str, version: str | None) -> None:
    from stoke.npm_check import resolve_npm_command
    npm_exe = shutil.which("npm")
    spec = f"{package}@{version}" if version else package
    result = subprocess.run(
        resolve_npm_command(npm_exe) + ["install", spec],
        cwd=str(config.config_path.parent),
    )
```

`stoke.toml`은 여전히 건드리지 않음 (JS/TS는 `package.json`이 진짜 매니페스트이고 stoke가 대체하지 않는다는 기존 원칙 유지) — 그냥 `npm install`을 사용자 대신 안전하게 실행해주는 것.

## 검증

scratchpad에 임시 JS 프로젝트(`stoke.toml` + `package.json`)를 만들고 `stoke add lodash` 실행:

```
Warning: npm 10.9.9 has a known Arborist bug ... fixed in npm 11.6.0.
  Using npx npm@11.19.1 for this install (global npm left untouched).
Running: npm install lodash
added 1 package, ...
```

`package.json`에 `"lodash": "^4.18.1"`이 정상 추가된 것까지 확인.

## 변경 파일

- `src/stoke/cli/deps.py`
