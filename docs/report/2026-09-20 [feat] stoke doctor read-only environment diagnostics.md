# stoke doctor -- 읽기 전용 환경 진단

- 날짜: 2026-09-20
- 종류: feat

## 배경

`npm doctor`/`flutter doctor`/`brew doctor`처럼, "빌드가 이상하게 안 되는데 뭐가 문제지"를 사람이 직접 하나씩 파봐야 하는 상황을 줄이려고 추가. `stoke build`도 문제를 잡아내긴 하는데 (1) 실제로 설치/컴파일까지 진행하는 무거운 동작이고 (2) 첫 번째 에러에서 멈춰버려서 문제가 여러 개면 한 번에 다 안 보여줌. `doctor`는 아무것도 설치/빌드하지 않고, 있는 문제를 최대한 한 번에 모아서 보여주는 게 목적.

## 변경

`src/stoke/doctor.py` 신규 (체크 로직) + `src/stoke/cli/doctor.py` 신규 (CLI):

- **entry/sources 존재 확인**: `target.entry`가 실제 파일로 존재하는지(없으면 error), `target.sources` glob이 최소 1개 파일과 매칭되는지(없으면 warn).
- **lock 파일 확인**: python/java/c/cpp(stoke가 직접 lock을 관리하는 언어)는 `stoke.lock` 존재 여부, stoke.toml에 선언된 버전(`python_version`/`java_version`)과 lock에 적힌 버전이 일치하는지, stoke.toml에 선언된 deps가 lock에 다 반영됐는지 확인.
- **네이티브 lock 파일 확인**: go/rust/js·ts/ruby/php는 stoke.lock을 안 쓰고 각자 생태계의 lock 파일(`go.sum`/`Cargo.lock`/`package-lock.json`/`Gemfile.lock`/`composer.lock`)을 쓰므로, 그것들의 존재 여부를 대신 확인. (go는 `go.mod`에 `require`가 없으면 애초에 `go.sum`이 안 생기는 게 정상이라, 그 경우엔 경고 안 함 — 테스트하다 이 오탐을 직접 발견해서 고침.)
- **툴체인 확인**: python은 venv 실행 파일 존재 + `pip freeze` 결과를 lock의 확정 버전과 비교(드리프트 감지). java/kotlin은 lock에 기록된 JAVA_HOME 디렉토리 존재 확인. c/cpp는 lock에 기록된 컴파일러 실행 파일 확인. go/rust/csharp/ruby/php는 `tool_install.toolchain_env`로 PATH/프로젝트 로컬 툴체인에서 실행 파일을 찾을 수 있는지 확인 (`stoke exec`가 찾는 것과 동일한 방식). js/ts는 `_node_tools.find_node` 재사용.
- **`.gitignore` 확인**: `lock_mode = "commit"`인데 `.gitignore`에 `stoke.lock`이나 `*.lock`이 그대로 들어있으면 경고 (재현 가능한 빌드라는 약속이 깨지는 흔한 실수).

각 체크는 `ok`/`warn`/`error` 레벨로 결과를 모으고, error가 하나라도 있으면 exit 1, 아니면 0.

## 검증

실제로 만들고 부수고 확인:
- **Go, 빌드 전**: lock/go.sum 관련 경고 정상 출력. 의존성 없는 프로젝트에서 `go.sum` 없음을 경고로 잘못 띄우는 걸 발견해서 `go.mod`에 `require`가 있을 때만 경고하도록 수정 (오탐 픽스).
- **Python, 빌드 후**: `stoke build`로 정상 상태 만든 뒤 `stoke doctor` → 전부 `ok`, exit 0.
- **Python, 고장낸 뒤**: venv 삭제 + entry 파일 삭제 → `entry 없음`(error), `sources 매칭 안 됨`(warn), `venv 없음`(warn) 전부 정상 출력, exit 1.
- **Python, 드리프트**: `six` 의존성 추가해서 빌드한 뒤 venv 안에서 `pip uninstall six`로 수동으로 지움 → "installed packages differ from lock file" 경고 정상 감지.

## 적용 안 한 것

- Kotlin은 java와 같은 JDK 체크로 처리 (Kotlin 전용 체크 없음 -- Gradle 자체의 문제는 stoke가 알 수 없는 영역).
- 프로젝트 전체(멀티 타겟/워크스페이스) 진단은 아직 없음 -- 지금은 `--target`으로 지정한 타겟 하나만.
