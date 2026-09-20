# stoke build/test --all -- 워크스페이스 멤버 전체 실행

- 날짜: 2026-09-20
- 종류: feat

## 배경

모노레포 작업(`stoke init --workspace` + `stoke new`) 때 미뤄뒀던 것. 워크스페이스를 만들어놓고 나면 결국 "서비스 3개를 하나씩 `cd`해서 빌드하기 귀찮다"는 문제가 남는데, 이번에 해결.

## 변경

`src/stoke/cli/workspace.py` 신규: `run_across_workspace(config, runner)`.

- `config.workspace`가 없으면(워크스페이스 루트가 아니면) 에러로 즉시 종료 -- "stoke init --workspace 먼저 하거나 서비스 디렉토리 안에서 실행하라"고 안내.
- `config.workspace.members`를 순회하며 각 서비스 서브디렉토리로 `os.chdir()`한 뒤 `runner()` 호출 -- `cmd_build`/`cmd_test`를 서브프로세스로 다시 실행하는 대신 함수를 직접 재사용 (같은 프로세스 안에서 cwd만 바꿔가며 호출). `cmd_build`/`cmd_test`는 내부적으로 `sys.exit()`을 쓰기 때문에, 멤버 하나가 실패해도 나머지가 안 돌지 않도록 `SystemExit`을 잡아서 계속 진행.
- 끝나면 실패한 멤버 목록을 모아서 출력하고, 하나라도 실패했으면 exit 1.

`stoke build`/`stoke test`에 `--all` 플래그 추가. **`stoke clean`에는 안 넣음** -- `clean`은 이미 `--all`을 "lock 파일까지 삭제"라는 뜻으로 쓰고 있어서 이름이 겹침. 워크스페이스 clean이 필요해지면 별도 플래그 이름으로 다시 고민.

## 검증

실제 2-서비스 워크스페이스(`backend`, `worker` 둘 다 Python)를 만들어서 확인:
- `stoke build --all` → 둘 다 독립적으로 venv 생성 + lock 저장 + 빌드 성공, `All 2 member(s) succeeded.` 출력.
- `backend/stoke.toml`을 일부러 깨뜨린 뒤 `stoke build --all` 재실행 → `worker`는 정상 빌드되고(멤버 하나 실패해도 나머지 계속 진행 확인), 최종적으로 `1/2 member(s) failed: backend` 출력하고 exit 1.
- 워크스페이스가 아닌 단일 프로젝트에서 `stoke build --all` 실행 → 명확한 에러 메시지로 즉시 종료 확인.

## 적용 안 한 것

- `stoke watch --all`/`stoke clean --all(워크스페이스 버전)` -- watch는 장기 실행 프로세스라 여러 개를 한 터미널에서 순차 실행하는 게 의미가 없고(백그라운드 병렬 실행은 별도 설계 필요), clean은 이름 충돌 문제로 보류.
- 병렬 실행 -- 지금은 순차 실행만. 멤버가 많아지면 병렬화가 필요해질 수 있음.
