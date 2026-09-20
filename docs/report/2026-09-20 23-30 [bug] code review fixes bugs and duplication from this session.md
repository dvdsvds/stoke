# 이번 세션 코드 전체 리뷰 후 버그/중복 정리

- 날짜: 2026-09-20
- 종류: bug

## 배경

이번 세션에서 대량으로 추가한 코드(audit/outdated/sbom/doctor/self-update/git/cache-server 등)에 대해 `/code-review high`를 세션 시작 시점(`a94ce35`)부터 `HEAD`까지 통째로 돌림. 10개 발견, 전부 실제 코드 확인 후 진짜인지 검증됨. 진짜 버그/보안 문제(1~6번)와 코드 중복(7~8번)을 수정. 효율성 문제(9~10번)는 정확성 문제가 아니라서 이번엔 보류.

## 고친 것

1. **워크스페이스 루트에서 타겟 없는 커맨드 실행 시 크래시** (`cli/utils.py`): `config.py`가 `[workspace]`가 있으면 `targets`가 비어도 통과하게 바꿔놨는데, `resolve_target_or_exit()`/`resolve_cpp_target()`은 여전히 `next(iter(config.targets))`를 기본값 없이 호출해서 `StopIteration`이 그대로 터짐(`stoke build`/`test`/`run`/`watch`/`exec`/`audit`/`outdated`/`sbom`/`doctor` 전부 해당). 빈 targets면 "워크스페이스 루트니까 멤버 디렉토리 안에서 실행하거나 --target/--all을 쓰라"는 깔끔한 에러로 교체.

2. **`stoke new`가 이름 검증 전에 디렉토리부터 만듦** (`cli/new_cmd.py`): `target_dir.mkdir()`이 `cmd_init_noninteractive`의 이름 검증(언어 스캐폴딩용 검증이지 디렉토리 경로 검증이 아님)보다 먼저 실행돼서, `stoke new "../../tmp/evil" -l python` 같은 이름이 의도한 부모 디렉토리 밖에 디렉토리를 만들 수 있었음. `_VALID_PROJECT_NAME`(letters/digits/-/_ only)로 디렉토리 생성 전에 먼저 검증하도록 수정.

3. **경로 탈출 방지 로직에 구분자 경계 누락 -- 3곳 동일 버그** (`cache_server.py`, `remote_cache.py`, `self_update.py`): `str(path).startswith(str(base_dir))` 패턴은 `/var/stoke-cache-evil`이 `/var/stoke-cache`로 시작한다는 이유로 통과시켜버림(디렉토리 경계 없는 문자열 prefix 비교). `Path.is_relative_to()`로 세 곳 다 교체. 이 프로젝트가 과거에 zip-slip 버그를 겪은 적이 있는데(`docs/report/`의 기존 문서), 같은 종류의 결함이 이번 세션에서 3번 재도입된 것.

4. **`stoke doctor`의 버전 비교가 "3.1"과 "3.10"을 같다고 오판** (`doctor.py`): `locked.version.startswith(declared_version)`이 문자열 prefix 비교라 `"3.10.4".startswith("3.1")`이 `True`가 되는 false negative가 있었음. 점(.) 단위로 쪼개서 비교하도록 수정.

5. **`add_workspace_member`의 TOML injection** (`toml_editor.py`): 멤버 이름을 이스케이프 없이 f-string으로 그대로 TOML에 꽂아 넣음. 이미 `add_dep()`이 같은 문제를 `_VALID_TOML_BARE_KEY` 검증으로 막아둔 전례가 있었는데 여기선 빠뜨렸음. `stoke new`가 이제 이름을 미리 검증하니(2번) 실질적 경로는 막혔지만, `add_workspace_member` 자체에도 같은 검증을 추가해서 방어를 이중화.

6. **`stoke build <target> --all`이 target을 조용히 무시** (`cli/__init__.py`): `--all`이 켜져 있으면 `args.target`을 아예 안 읽어서, 특정 타겟만 빌드하려던 사용자가 모르는 새 워크스페이스 전체를 빌드하게 됨. 두 옵션을 같이 주면 명확한 에러로 거부하도록 수정 (`build`/`test` 둘 다).

## 중복 정리한 것

7. **TypeScript dev-server 프레임워크 6곳에 복붙된 `_write_stoke_toml`** (hono/nestjs/nextjs/nuxt/sveltekit/vite): `run_script` 값만 다르고 완전히 동일한 함수가 6번 복붙돼 있었음. `_node_tools.py`에 `write_dev_server_stoke_toml(project_path, project_name, run_script="dev")` 공용 함수로 추출, 6개 파일 전부 이걸 쓰도록 변경.

8. **`audit.py`/`outdated.py`의 대규모 중복**: `_emit_raw_json`이 두 파일에 바이트 단위로 동일, `_audit_json_wrapped_external`/`_outdated_json_wrapped_external`이 이름만 다르고 로직 동일, dotnet csproj 탐색/dotnet 실행파일 탐색 로직도 동일. `cli/_dep_check.py`(새 내부 전용 모듈)로 `emit_raw_json`/`json_wrapped_external`/`find_dotnet`/`find_csproj` 추출, 두 파일 다 여기서 import해서 씀.

## 검증

- **버그 1**: 워크스페이스 루트에서 `stoke build` 실행 → 전에는 `StopIteration` 트레이스백, 지금은 깔끔한 에러 메시지 + exit 1 확인.
- **버그 2**: `stoke new "../../tmp/evil" -l python` 실행 → 에러로 거부되고 `/tmp/tmp/evil` 디렉토리가 실제로 안 생긴 것 확인.
- **버그 3**: `/tmp/stoke-cache`(cache_dir)와 `/tmp/stoke-cache-evil/x`(sibling)로 old prefix-비교 방식(`True`, 취약)과 new `is_relative_to`(`False`, 안전) 둘 다 실제로 실행해서 차이 확인.
- **버그 4**: `"3.1"`/`"3.10.4"`(전엔 오탐 아님, 지금은 mismatch로 정확히 감지), `"3.12"`/`"3.12.4"`(정상 일치), `"3.9"`/`"3.12.4"`(정상 불일치) 세 케이스 직접 실행해서 확인.
- **중복 정리 7**: `write_dev_server_stoke_toml`을 직접 호출해서 기존과 바이트 단위로 동일한 출력이 나오는 것 확인, 실제로 `stoke init vite`를 끝까지 돌려서(`npm create vite@latest` 포함) 정상적으로 `stoke.toml`이 생기는 것도 확인.
- **중복 정리 8**: 리팩터 후 `stoke audit`/`stoke audit --json`/`stoke outdated`를 가짜 lock 파일로 다시 돌려서 회귀 없음 확인 (실제 OSV.dev 취약점 8개, 최신 버전 비교까지 전부 이전과 동일하게 동작).

## 적용 안 한 것

- **직렬 네트워크 호출** (`osv.py`의 `_fetch_summaries`, `outdated.py`의 `pypi_latest`/`maven_latest` 조회) -- CVE/패키지 개수가 많을 때 순차 조회라 느려짐. 정확성 문제는 아니라서 보류, `ThreadPoolExecutor`로 병렬화하면 될 것으로 보임.
- **`cache_server.py`의 `do_PUT`이 업로드 전체를 메모리에 올림 + 원자적 쓰기 로직이 `remote_cache.py`와 중복** -- 동시 다중 업로드 시 메모리 사용량 문제 가능성. 스트리밍 재작성은 범위가 더 커서 보류.
