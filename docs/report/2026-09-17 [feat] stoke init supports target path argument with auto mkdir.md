# stoke init에 경로 인자 추가

- 날짜: 2026-09-17
- 종류: feat
- 요청: `stoke init [type] [path]`가 안 됨. 경로 지정 기능 추가, 경로가 없으면 디렉토리 자동 생성.

## 변경 전

`stoke init` 은 항상 현재 디렉토리(`Path.cwd()`) 기준으로만 동작했음. 다른 위치에 프로젝트를 만들려면 사용자가 직접 `mkdir <dir> && cd <dir> && stoke init <type>`을 해야 했음.

## 변경 후

```
stoke init express korea-notify-api/
```

- `init` 서브커맨드에 두 번째 선택적 위치 인자 `path` 추가.
- `path`가 주어지면 `mkdir(parents=True, exist_ok=True)`로 디렉토리를 생성(이미 있으면 그대로 사용)한 뒤 `os.chdir()`로 이동하고, 그 다음에 기존 init 핸들러를 그대로 호출.
- 모든 프레임워크 핸들러(`cmd_init_express` 등)와 `cmd_init`/`cmd_init_noninteractive`가 내부적으로 `Path.cwd()` 기준으로 동작하고 있었기 때문에, 핸들러들을 개별로 고칠 필요 없이 CLI 진입점에서 `chdir`만 해주는 것으로 전체에 적용됨.

## 변경 파일

- `src/stoke/cli/__init__.py`
  - `init_parser`에 `path` 위치 인자 추가
  - `args.command == "init"` 분기에서 `path` 있으면 mkdir + chdir 후 기존 로직 실행
