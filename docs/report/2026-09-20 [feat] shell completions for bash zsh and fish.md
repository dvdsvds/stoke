# stoke completions -- bash/zsh/fish 셸 자동완성

- 날짜: 2026-09-20
- 종류: feat

## 배경

"실무 트렌드를 따라가자"에서 나온 두 번째 항목. 진지하게 쓰이는 CLI 도구(`cargo`, `gh`, `docker`, `kubectl` 등)는 거의 다 셸 자동완성을 제공함 — 없으면 그 자체로 "덜 성숙한 도구"라는 인상을 줌. `stoke self-update`와 마찬가지로 실무 트렌드 목록 중 구현 비용이 가장 낮은 항목이라 먼저 선택됨.

## 설계

명령어/플래그 목록을 손으로 따로 관리하면 새 서브커맨드가 추가될 때마다(이번 세션에만 `audit`/`outdated`/`sbom`/`doctor`/`new`/`self-update`/`completions` 7개가 새로 생김) 자동완성 스크립트가 계속 어긋날 위험이 있음. 그래서 완성 스크립트를 손으로 안 쓰고, **`_build_parser()`가 만드는 실제 argparse 구조를 리플렉션해서 그때그때 생성**하도록 함 (`stoke completions <shell>` 실행 시점 기준 스냅샷).

타겟 이름(`stoke build <TAB>`, `stoke audit --target <TAB>`) 같은 동적 값은 스크립트 생성 시점에 알 수 없으니, 셸 스크립트가 자동완성 시점에 **`stoke complete-targets`라는 숨김 명령을 다시 호출**해서 현재 디렉토리의 `stoke.toml`을 읽어 타겟 이름을 실시간으로 받아오게 함 (`argparse` subparser의 help listing에서는 제거하되 `.choices`엔 남겨서 실행은 되게 처리 -- `help=argparse.SUPPRESS`가 서브커맨드 목록에서는 실제로 안 먹힌다는 걸 테스트하다 발견해서, `subparsers._choices_actions`에서 직접 제거하는 방식으로 우회함).

## 변경

`src/stoke/cli/completions.py` 신규:

- `_introspect()` -- `_build_parser()`의 `_SubParsersAction.choices`를 순회해서 `{명령어: [플래그...]}` 딕셔너리 생성.
- `cmd_complete_targets()` -- `stoke complete-targets` (숨김): 현재 `stoke.toml`의 타겟 이름을 한 줄씩 출력, 실패하면 조용히 아무것도 안 함(자동완성 중 에러 메시지가 뜨면 안 되니까).
- **bash**: `COMP_WORDS`/`compgen` 기반 순수 bash 스크립트 (bash-completion 패키지 의존성 없음).
- **fish**: `complete -c stoke -n "__fish_seen_subcommand_from ..."` 라인들.
- **zsh**: 네이티브 `_arguments` 스크립트를 손으로 새로 짜는 대신, `bashcompinit`으로 위의(실제로 검증된) bash 스크립트를 그대로 재사용. 이 환경에 zsh가 없어서(`apt-get install zsh`도 권한 없어서 실패) 손으로 짠 zsh 전용 스크립트를 검증할 방법이 없었음 -- 검증 안 된 코드를 새로 짜기보다 이미 테스트로 확인된 bash 스크립트를 재사용하는 쪽을 택함.
- `stoke completions <bash|zsh|fish>` -- 스크립트를 stdout에 출력, 설치 방법 안내는 stderr로 (스크립트 자체가 `source <(...)`로 그대로 실행 가능하게).

## 검증

**bash**: 생성된 스크립트를 실제로 `source`한 뒤 `COMP_WORDS`/`COMP_CWORD`를 손으로 설정해서 `_stoke_completions` 함수를 직접 호출하는 방식으로 검증 (완전히 표준적인 bash completion 테스트 방법). 확인한 것:
- 최상위 명령어 부분완성: `stoke bui<TAB>` → `build`
- 플래그 완성: `stoke build --f<TAB>` → `--force`
- **동적 타겟 완성** (가장 중요한 부분): 실제 `stoke.toml`이 있는 테스트 프로젝트를 만들고, `stoke`를 PATH에 얹은 뒤 `stoke build <TAB>` → `myproj`(실제 타겟 이름), `stoke audit --target <TAB>` → `myproj` 정상 확인.

**fish**: `complete -C"stoke ..."` (fish가 지원하는 비대화형 자동완성 시뮬레이션 명령)으로 동일하게 검증 -- 최상위 명령어, 플래그, 동적 타겟 이름 전부 정상 출력 확인.

**zsh**: 검증 못 함 (환경에 zsh 없음, 설치 권한도 없음) -- 위에서 설명한 대로 검증된 bash 스크립트 재사용으로 리스크를 낮춤.

테스트 중 `help=argparse.SUPPRESS`가 서브커맨드 목록에서 실제로는 숨겨지지 않고 `==SUPPRESS==`라는 문자열이 그대로 노출되는 버그를 발견해서, `subparsers._choices_actions`를 직접 조작하는 방식으로 우회 수정함.

## 적용 안 한 것

- zsh 네이티브 `_arguments` 스크립트 -- 검증 환경이 없어서 bashcompinit 우회로 대체. 나중에 zsh 있는 환경에서 확인 후 네이티브로 바꿀 수 있음.
- `stoke init <TAB>`의 프레임워크 타입 이름(`fastapi`, `express` 등) 자동완성 -- `type` positional은 이미 `choices=` 목록이 있어서 argparse 자체가 알고 있지만, 이번 completions.py는 플래그(`--xxx`)만 다루고 명령어별 positional choices까지는 아직 안 뽑아냄. 다음 개선 후보.
