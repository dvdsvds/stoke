# 모노레포: stoke init --workspace + stoke new

- 날짜: 2026-09-20
- 종류: feat

## 배경

"모노레포 지원이 부실하다"는 외부 지적으로 시작한 조사에서, 실제 원인을 찾음: `stoke.toml`의 `[targets.*]` 자체는 원래부터 여러 개를 지원하지만(`config.py`가 dict로 파싱), `stoke.lock`(`lock.py`)은 언어당 슬롯이 하나뿐(`python`, `java`, `c`, `cpp` 각각 `X | None` 하나씩)이라 **같은 언어 타겟이 2개 이상이면 lock 파일이 서로 덮어써지는 버그**가 있었음. `lock.py`의 `save_lock`에 "다중 언어 타겟이 lock 파일 하나를 공유"라는 주석이 이 설계를 명시하고 있었음 — 애초에 같은 언어 다중 타겟은 고려 대상이 아니었음.

## 논의된 대안과 선택 이유

1. lock 파일을 타겟별로 키 분리 (breaking change, lock 파일 포맷 자체를 바꿔야 함)
2. `stoke target add` 같은 명령으로 기존 `stoke.toml`에 타겟 추가 (12개 언어 각각의 `_write_stoke_toml_<lang>` 함수가 전부 "새 파일 통째로 쓰기" 전제라 리팩터 비용 큼, 서브디렉토리 규칙도 별도로 필요)
3. **서비스마다 독립된 `stoke.toml`/`stoke.lock`을 서브디렉토리로 분리** — lock 슬롯 충돌 문제 자체가 발생하지 않음, 기존 언어별 init 로직을 그대로 재사용 가능

3번으로 결정. 대신 "서비스 여러 개를 매번 수동으로 mkdir + cd + stoke init 하기 번거롭다"는 문제가 남아서, 이를 묶어주는 워크스페이스 루트 개념을 추가.

## 변경

- `src/stoke/config.py`: `Workspace` dataclass 추가 (`members: list[str]`), `Config.workspace` 필드. `[workspace]` 섹션이 있으면 `[targets.*]` 없어도 되도록 검증 예외 처리.
- `src/stoke/init.py`: `cmd_init_workspace(project_name, yes)` 추가 -- 언어/타겟 없는 루트 `stoke.toml`(`[workspace] members = []`)만 씀.
- `src/stoke/cli/new_cmd.py` 신규: `cmd_new(name, language, version, ...)` -- `<name>/` 서브디렉토리 생성 → 그 안에서 기존 `cmd_init_noninteractive` 그대로 재사용(마치 `tool_install._prompt_and_install`의 chdir 패턴과 동일) → 부모 디렉토리에 워크스페이스 루트 `stoke.toml`이 있으면 `members`에 자동 등록.
- `src/stoke/toml_editor.py`: `add_workspace_member(toml_path, name)` 추가 -- `add_dep`과 같은 정규식 기반 TOML 편집 패턴 (tomllib이 읽기 전용이라 쓰기는 항상 문자열 편집).
- CLI: `stoke init -w/--workspace`, `stoke new <name> -l <language> [-V <version>] [--env-type] [--lock-mode] [--vcpkg]` 서브커맨드 추가. `stoke init`의 기존 `--language`/`--version`에 `-l`/`-V` 단축 플래그도 추가 (긴 플래그는 유지, 하위호환).
  - `-v`는 `stoke build`/`watch`/`run`/`test`/`hot-reload`에서 이미 `--verbose`로 쓰이고 있어서, 버전 단축은 대문자 `-V`로 분리 (같은 글자가 명령어마다 다른 뜻이 되는 걸 피함).

## 검증

실제로 만들어서 확인:
```
stoke init -w --name=my-company
stoke new backend -l python -V 3.12
stoke new worker  -l python -V 3.11
```
→ `backend/stoke.toml`(python 3.12), `worker/stoke.toml`(python 3.11) 독립 생성, 루트 `stoke.toml`의 `members`에 둘 다 자동 등록됨을 확인. `load_config()`로 워크스페이스 루트가 `targets={}`, `workspace.members=[...]`로 정상 파싱되는 것도 확인. 워크스페이스 밖에서 `stoke new`를 단독 실행해도 정상 동작(그냥 서브디렉토리만 생성) 확인.

테스트 중 `add_workspace_member`의 정규식(`\s*$`)이 파일 끝 개행 문자를 같이 삼켜버려서 `stoke.toml`의 trailing newline이 사라지는 버그를 발견 → `[ \t]*$`로 수정.

## 적용 안 한 것

- `stoke build/test/watch/clean --all` (워크스페이스 멤버 전체 순회 실행) -- 다음 단계로 남김. 지금은 각 서비스 디렉토리에서 개별 실행.
