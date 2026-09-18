# `stoke add`/`stoke remove`(JS/TS)가 프로젝트 로컬 Node 툴체인을 무시하고 시스템 PATH만 봄

- 날짜: 2026-09-18
- 심각도: high
- 상태: 수정됨

## 배경

사용자가 `stoke init bubbletea`로 만든 프로젝트에서 `go mod tidy`가 안 되는 걸 겪음 — 원인은 stoke가 Go를 `.stoke/toolchains/go-1.26.5/`에 프로젝트 전용으로 설치했을 뿐 시스템 PATH엔 없어서, `stoke build`(내부적으로 툴체인 경로를 직접 호출)는 되는데 사용자가 셸에서 직접 치는 `go mod tidy`는 시스템 PATH를 보니 실패한 것. 이 클래스의 문제가 다른 언어에도 있는지 전수 조사하다가 발견함.

## 조사 결과 — 정상인 부분

Go/Rust/C#/Ruby/PHP/Node.js 전부 **stoke 자체의 build/run/test 경로**는 일관되게 `.stoke/toolchains/<lang>-*/`를 PATH보다 먼저 찾도록 구현돼 있음:

- `go/adapter.py: _find_go()`
- `rust/adapter.py`
- `csharp/adapter.py`
- `ruby/adapter.py: _find_ruby() / _find_bundle()`
- `php/adapter.py`
- `_node_tools.py: NodeToolsMixin._find_node() / _find_npm()` (javascript/typescript 어댑터가 공유)

여긴 문제 없음.

## 문제 — `stoke add`/`stoke remove`만 다른 방식으로 구현됨

`src/stoke/cli/deps.py`의 `_NATIVE_HINT`(37-46행)를 보면, go/rust/csharp/ruby/php/kotlin은 `stoke add`가 그냥 "네이티브 도구 쓰세요" 힌트만 찍고 끝남(예: `"go": "go get <module>"`) — 실제로 명령을 실행하지 않으므로 이 클래스의 버그가 없음.

반면 JavaScript/TypeScript는 stoke가 **직접 npm을 실행해주겠다고 약속**함(`_npm_add`, `_npm_remove`, `deps.py:31-47, 100-113`). 그런데 이 두 함수는:

```python
npm_exe = shutil.which("npm")
if npm_exe is None:
    print("Error: npm not found in PATH.", file=sys.stderr)
    sys.exit(1)
```

시스템 PATH만 보고 끝남. 반면 build/run이 쓰는 올바른 resolver(`_node_tools.py`의 `NodeToolsMixin._find_npm()`)는 프로젝트 로컬 `.stoke/toolchains/nodejs-*/` 먼저, 없으면 PATH를 보는 방식으로 이미 구현돼 있는데, `deps.py`는 이걸 재사용하지 않고 따로 `shutil.which`만 호출하도록 구현되어 있음.

**결과**: Node.js를 `stoke install --language=nodejs`로만 설치하고 시스템에 별도로 설치하지 않은 환경에서 —
- `stoke build` / `stoke run` — 정상 동작
- `stoke add <package>` / `stoke remove <package>` — "Error: npm not found in PATH"로 항상 실패

다른 언어는 애초에 stoke가 명령을 대신 안 실행하니 이 문제가 없는데, JS/TS만 "대신 실행해준다"고 특별 취급한 코드 경로에서 리소스 탐색 로직만 빠뜨린 형태.

## 재현 위치

- `src/stoke/cli/deps.py:37` (`_npm_add` 내부 `shutil.which("npm")`)
- `src/stoke/cli/deps.py:105` (`_npm_remove` 내부 `shutil.which("npm")`, 정확한 줄 번호는 파일 참고)

## 수정

`src/stoke/languages/_node_tools.py`의 탐색 로직을 모듈 레벨 함수(`find_local_node_dir`/`find_node`/`find_npm`)로 추출하고, `NodeToolsMixin`의 기존 메서드들은 이 함수들을 호출하는 얇은 래퍼로 유지(기존 어댑터 호출부는 변경 없음). `src/stoke/cli/deps.py`의 `_npm_add`/`_npm_remove`가 `shutil.which("npm")` 대신 새 `find_npm(project_root)`를 쓰도록 변경 — `project_root`는 `config.config_path.parent`. `RuntimeError`를 잡아서 기존과 동일한 형태(`Error: ...`, exit 1)로 출력하도록 함.

결과: Node.js를 `stoke install --language=nodejs`로만 설치한 프로젝트에서도 `stoke add`/`stoke remove`가 `stoke build`/`run`과 동일하게 `.stoke/toolchains/nodejs-*/`를 먼저 찾아서 정상 동작함.
