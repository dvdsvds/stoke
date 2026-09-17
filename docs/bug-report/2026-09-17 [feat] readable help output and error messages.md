# --help / 에러 메시지 가독성 개선

- 날짜: 2026-09-17
- 종류: feat

## 문제

`stoke --help`, `stoke install --help`, `stoke init --help` 등에서 서브커맨드/선택지 목록이 `{build,python,java,c,cpp,install,uninstall,vcpkg,clean,init,watch,run,test,add,remove,ide-sync,hot-reload}` 처럼 전부 한 줄에 붙어서 나와 읽기 힘들었음. 특히 `stoke init --help`는 프레임워크 24개가 한 줄에 다 붙어서 거의 못 읽는 수준이었음.

`stoke help`처럼 자연스럽게 칠 법한 명령도 도움말 대신 argparse의 `invalid choice: 'help' (choose from build, python, java, ...)` 에러가 떴고, 이 에러 메시지도 후보들이 한 줄에 콤마로 다닥다닥 붙어서 나왔음.

## 변경

`src/stoke/cli/__init__.py`:

- `_help_formatter(prog)`: 터미널 폭에 맞춰(최대 100컬럼) `max_help_position=32`로 넓힌 `HelpFormatter`. 모든 `add_parser()` 호출에 `formatter_class=_help_formatter` 적용(정규식으로 일괄 치환, 25곳).
- 메인 `subparsers`와 `vcpkg_sub`에 `metavar="<command>"` 지정 — usage 줄의 `{build,python,...}` 긴 나열 대신 `<command>` 하나로 축약. 서브커맨드 목록 자체는 그 아래 itemized 목록(설명 포함)에서 이미 다 보여주므로 정보 손실 없음.
- `install`/`uninstall`의 `tool` 위치 인자, `init`의 `type` 위치 인자에 `metavar="<tool>"`/`<type>` 지정 — 특히 `init`은 프레임워크 24개가 usage/help에 그대로 나열되던 걸 없앰.
- `_StokeArgumentParser(argparse.ArgumentParser)`: `error()`를 오버라이드해서 `invalid choice: 'X' (choose from a, b, c, ...)` 형태의 메시지를 감지하면, 후보를 한 줄에 하나씩 출력하도록 재포맷. 최상위 `parser`를 이 클래스로 만들면 `add_subparsers()`가 기본적으로 `type(self)`를 `parser_class`로 쓰기 때문에 모든 하위 서브파서(`install`, `python list` 등)에도 자동으로 적용됨.
- `stoke help` / `stoke help <command>`: `main()`에서 `sys.argv[1] == "help"`를 감지해 `["--help"]`(또는 `[<command>, "--help"]`)로 바꿔 `parse_args`에 넘김 — 에러 대신 해당 도움말을 그대로 보여줌.

## Before / After

**Before**:
```
usage: stoke [-h] [-V]
             {build,python,java,c,cpp,install,uninstall,vcpkg,clean,init,watch,run,test,add,remove,ide-sync,hot-reload} ...
...
stoke: error: argument <command>: invalid choice: 'help' (choose from build, python, java, c, cpp, install, uninstall, vcpkg, clean, init, watch, run, test, add, remove, ide-sync, hot-reload)
```

**After**:
```
usage: stoke [-h] [-V] <command> ...
...
stoke help
  → 도움말 그대로 출력, 에러 아님

stoke badcmd
usage: stoke [-h] [-V] <command> ...
stoke: error: 'badcmd' isn't a valid <command>. Choose from:
  build
  python
  java
  ...
```

## 검증

`stoke --help`, `stoke install --help`, `stoke init --help`, `stoke vcpkg --help`, `stoke help`, `stoke help build`, `stoke badcmd`, `stoke install badlang` 전부 실제로 실행해서 출력 확인함.

## 변경 파일

- `src/stoke/cli/__init__.py`
