# stoke git -- add/commit/push 대화형 메뉴

- 날짜: 2026-09-20
- 종류: feat

## 배경

git init/GitHub 원격 생성(`stoke init`에 추가된 기능) 작업 하던 중 이어진 아이디어: git 플래그(`-m`, `-u origin`, 브랜치 문법 등) 외우기 싫어하는 사람들을 위해 `stoke init`처럼 대화형으로 add/commit/push를 할 수 있는 메뉴를 만들자는 것.

## 설계 논의 (여러 번 방향이 바뀜)

- 처음엔 `stoke commit`/`stoke push`를 각각 별도 서브커맨드로 생각했는데, 최종적으로는 **`stoke git` 하나로 통합**하고 그 안에서 메뉴로 add/commit/push를 고르는 방식으로 정리됨.
- `git add`용 서브커맨드 이름으로 `add`를 쓰려다가, `stoke add`가 **이미 Python/Java 의존성 추가 명령으로 선점**돼 있는 걸 확인하고 폐기 -- 별도 `add`류 서브커맨드는 안 만들고, `stoke git` 메뉴 안의 선택지("Add files")로만 존재.
- 파일 스테이징은 `git add .`(전체) 하나로 가지 않고, **체크박스 UI로 파일을 골라서** add하는 쪽으로 감 (전체 선택도 가능, 기본은 전부 체크된 상태로 시작).
- 커밋 해시는 커밋을 만들기 전엔 존재하지 않는 값이라, 커밋 **완료 후**에 `git rev-parse --short HEAD`로 읽어와서 `----- <해시> -----` 형식으로 보여주는 걸로 정리.
- 메뉴가 액션 하나 실행하고 끝나는 게 아니라, **Exit을 고를 때까지 반복**되는 루프로 구현 (add → commit → push를 한 세션 안에서 이어서 할 수 있게).

## 변경

`src/stoke/prompts.py`에 `_prompt_checkbox()` 신규 -- 여러 개 고르는 프롬프트(TUI는 questionary의 체크박스, 스페이스바로 토글; 비대화형/폴백은 번호 여러 개 공백으로 구분 입력 또는 `a`로 전체 선택). 기존 `_prompt`/`_prompt_choice`/`_prompt_yes_no`와 같은 패턴(TUI 되면 questionary, 안 되면 번호 입력 폴백).

`src/stoke/git_setup.py`에 추가:
- `get_changed_files()`/`get_staged_files()` -- `git status --porcelain`/`git diff --cached --name-only` 파싱.
- `git_add()`/`git_commit()`(성공하면 짧은 해시, 실패하면 에러 메시지 반환)/`current_branch()`/`list_branches()`/`git_push()`(HEAD를 `origin/<branch>`로, 없으면 새로 생성하면서 push).

`src/stoke/cli/git_cmd.py` 신규: `cmd_git()` -- 먼저 `find_parent_git_repo()`로 git 저장소 안인지 확인(아니면 에러), 그 다음 "On branch 'X', N file(s) changed." 상태 표시 + 메뉴(Add files/Commit/Push/Exit) 반복 루프.

`stoke git` 서브커맨드로 등록 (`stoke add`와 이름 충돌 없음 확인됨).

## 검증

실제 로컬 git 저장소 + 로컬 bare 저장소(가짜 원격)로 전체 플로우를 스크립팅된 입력으로 끝까지 돌려봄:
- **Add**: 체크박스에서 파일 2개 다 선택(`a`) → "Added 2 file(s)." 확인.
- **Commit**: 메시지 입력 → `----- 8df55c2 -----` 형태로 실제 해시 출력, "Committed." 확인.
- **Push**: 브랜치 선택(현재 브랜치가 기본값으로 표시) → 실제로 로컬 bare 저장소(`/tmp/.../remote.git`)에 push됨 → **원격 쪽에서 `git log`로 커밋 해시/메시지가 정확히 도착한 것까지 확인**.
- **Exit**: 메뉴 루프가 정상 종료, exit code 0.
- **엣지 케이스**: git 저장소가 아닌 디렉토리에서 실행 → 명확한 에러(exit 1). 커밋할 게 없는데 Commit 선택 → "Nothing staged -- use 'Add files' first." 안내 후 메뉴로 복귀. 둘 다 확인.

## 적용 안 한 것

- Pull/fetch/status 같은 다른 git 동작 -- 이번엔 add/commit/push 세 개만 (사용자가 명시적으로 요청한 범위).
- 커밋 메시지 템플릿/conventional commits 강제 -- 그냥 자유 텍스트 입력.
