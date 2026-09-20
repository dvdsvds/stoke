# stoke init에 git 저장소 초기화 + GitHub 원격 생성 추가

- 날짜: 2026-09-20
- 종류: feat

## 배경

`cargo new`/`npm create` 같은 도구들이 기본으로 `git init`을 해주는 것처럼, stoke도 프로젝트 스캐폴딩 직후 git 저장소를 바로 쓸 수 있게 하자는 아이디어. stoke는 이미 `stoke build`가 `.gitignore`를 관리하고 있어서(예: `.stoke/` 추가) 사실 "git 저장소가 있다"는 걸 암묵적으로 전제하고 있었는데, 정작 그 저장소를 만들어주지는 않았음 — 빠진 조각을 채운 것.

## 설계 논의

- **git 저장소 생성만 기본값으로 갈지, GitHub 원격 생성까지 자동으로 할지**를 사용자와 상의: 로컬 `git init`은 위험이 낮아서(외부에 아무것도 안 생김) 기본 흐름에 넣기로, GitHub 원격 생성(`gh repo create`)은 실제로 외부에 뭔가가 생기는 작업이라 **매번 명시적으로 물어보는 별도 질문**으로 분리.
- **초기 스캐폴딩 결과물은 자동 커밋함** (처음엔 "자동 커밋은 안 함, 사용자가 직접 리뷰"로 갔다가 사용자 피드백으로 방향 전환). `README.md`를 추가로 생성하고 `git add -A && git commit`까지 실행. `lock_mode`(`commit`/`local`)에 따라 커밋 대상을 다르게 가려야 하나 고민했는데, 실제로는 불필요 — lock 파일 자체가 init 시점엔 아직 존재하지 않고(첫 `stoke build`에서 생김), `.gitignore`도 build 시점에 생기기 때문에 init 시점엔 `lock_mode` 값이 커밋 내용에 아무 영향을 안 줌. 그냥 항상 커밋하면 됨.
- **Linux/macOS를 합쳐도 되는지** 논의 후 분리하기로 함 — macOS는 Homebrew 하나로 거의 통일되지만(또는 애초에 Xcode Command Line Tools로 git이 이미 깔려있는 경우가 많음), Linux는 배포판마다 패키지 매니저가 다름(apt/dnf/pacman/zypper/apk). git이 시스템에 없을 때만 설치를 제안하고, 이건 stoke가 유일하게 프로젝트 로컬이 아니라 **시스템 전역**에 설치하는 경우임 (다른 언어 툴체인은 전부 `.stoke/toolchains/`에 격리되는데, git은 원래 시스템 전역에 있는 게 정상이라 예외로 둠).
- **부모 디렉토리 검사**: 이미 git 저장소 안(상위 디렉토리에 `.git` 있음)이면 중첩 저장소가 생기지 않게 질문 자체를 스킵.
- **GitHub 소유자(계정/조직) 선택**: `gh api user/orgs`로 사용자가 속한 조직 목록을 가져와서 개인 계정과 함께 선택지로 제시. 저장소 이름이 이미 존재하면(`gh repo view owner/name`) 다른 이름을 다시 물어봄.

## 변경

`src/stoke/git_setup.py` 신규:

- `find_parent_git_repo(start)` -- 상위 디렉토리로 올라가며 `.git` 탐색.
- `is_git_installed()`/`install_git_globally()` -- OS별(Windows: winget, macOS: brew 있으면 brew 없으면 xcode-select 안내, Linux: apt-get/dnf/pacman/zypper/apk 중 있는 것) 시스템 전역 설치 시도, 실패하면 수동 설치 안내로 폴백.
- `git_init(project_dir)` -- `git init` 실행.
- `git_commit_all(project_dir, message)` -- `git add -A` + `git commit`.
- `is_gh_available()`/`list_github_owners()`/`github_repo_exists()`/`create_github_remote()` -- GitHub CLI(`gh`) 기반. `gh`가 없거나 로그인 안 돼 있으면 원격 생성 단계 전체를 조용히 스킵.

`src/stoke/init.py`의 대화형 `cmd_init()`에 `_prompt_git_setup()`(프로젝트 이름 입력 직후, 언어 선택 전에 질문)과 `_apply_git_setup()`(모든 파일이 다 쓰인 뒤 맨 마지막에 실제 실행 -- `git init` → `README.md` 생성 → 초기 커밋 → 선택했으면 GitHub 원격 생성 순서) 추가. `_write_readme()`는 이미 `README.md`가 있으면 안 건드림.

## 검증

실제로 다 돌려봄:
- **부모 디렉토리 검사**: 이미 git 저장소인 디렉토리 안의 서브디렉토리에서 `stoke init` → "Already inside a git repository (...) -- skipping git init." 뜨고 질문 자체가 안 나오는 것 확인.
- **`find_parent_git_repo`/`is_git_installed`/`is_gh_available`/`list_github_owners`/`github_repo_exists`**: 이 저장소(dvdsvds/stoke)와 실제 GitHub API로 전부 검증 (존재하는 저장소는 True, 존재 안 하는 이름은 False).
- **`git_init`**: 임시 디렉토리에서 실제로 `.git` 생성되는 것 확인.
- **전체 마법사 플로우**: `printf`로 입력을 스크립팅해서 "Initialize a git repo? [Y/n]" / "Create a GitHub remote too? [y/N]"이 프로젝트 이름 입력 직후, 언어 선택 전에 정확히 뜨는 것 확인. (초기엔 "자동 커밋 안 함"으로 구현해서 `git log`가 "does not have any commits yet"인 것까지 확인했다가, 방향 전환 후 재검증함.)
- **자동 커밋 + README (방향 전환 후 재검증)**: `lock_mode="local"`로 마법사를 끝까지 돌려서, `git init` 직후 `README.md`(프로젝트 이름 들어간 내용)가 생기고, `git log --stat`에 `README.md`/`stoke.toml`/`src/main.py` 3개 파일이 담긴 커밋이 실제로 생기는 것 확인. `lock_mode`가 `commit`이든 `local`이든 init 시점엔 커밋 대상에 차이가 없다는 것도 확인(둘 다 lock 파일이 아직 없어서).
- **실제 GitHub 저장소 생성(`create_github_remote`)은 사용자가 직접 테스트** — 실제로 생성 성공 확인됨.

## 적용 안 한 것

- 비대화형 `stoke init --language=X` 모드에 `--git`/`--remote` 플래그 추가 -- 이번엔 대화형 마법사만. 필요하면 다음 단계로.
- `create_github_remote()`가 GitHub 저장소 생성에 실패하는 다양한 케이스(권한 부족, 조직 정책으로 개인이 저장소 못 만드는 경우 등)의 에러 메시지 세분화 -- 지금은 `gh`가 뱉는 stderr를 그대로 보여주는 수준.
