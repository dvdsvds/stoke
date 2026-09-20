# 프로젝트 이름이 전혀 검증 안 됨 — stoke.toml 및 생성 코드가 깨질 수 있음

- 날짜: 2026-09-17
- 심각도: high (cross-cutting, 거의 모든 프레임워크에 영향)
- 상태: 수정됨

## 문제

`src/stoke/prompts.py:195-217`의 `resolve_project_name()`/`resolve_project_dir()`가 사용자 입력을 그대로 받고 아무 검증도 안 함 (charset, 길이, `/`, `..`, 공백, 따옴표, 셸 메타문자 전부 무검증). `resolve_project_name`은 cwd가 비어있으면 기본값을 `cwd.name`으로 쓰는데, 이건 사용자가 실제로 지을 법한 폴더 이름("My App" 등)이 그대로 들어간다는 뜻.

이 값이 이후 아무 이스케이프 없이 여러 곳에 흘러들어감:

### 1. `[targets.{project_name}]` TOML 헤더가 깨짐 (11개 파일)

f-string으로 직접 박아 넣음 (TOML 안전 인코더 아님):

- `python/frameworks/{fastapi,flask,django}.py`
- `go/frameworks/{gin,echo,fiber,chi}.py`
- `rust/frameworks/{actix_web,axum,rocket}.py`
- `kotlin/frameworks/{ktor,spring_boot}.py`
- `csharp/frameworks/aspnet_core.py`
- `ruby/frameworks/sinatra.py`
- `php/frameworks/slim.py`
- `javascript/frameworks/{express,fastify}.py`

프로젝트 이름에 공백이 있으면(`my app`) `[targets.my app]`은 **유효하지 않은 TOML**이라 스캐폴딩은 성공했다고 나오는데 바로 다음 `stoke build`가 파싱 에러로 깨짐. 점(`.`)이 있으면(`my.app`) TOML이 이걸 중첩 테이블로 해석해서 `targets.my.app`이 `[project] name = "my.app"`과 어긋남. `"`가 있으면 문자열 리터럴 자체가 깨짐.

### 2. 생성된 소스 코드가 깨짐

- Go: `module_name`이 `"{module_name}/handlers"` import 문자열에 그대로 들어감 (`gin.py:81` 등) — `"`가 있으면 문법 에러 나는 `main.go` 생성
- Kotlin Spring Boot: `package_name = project_name.lower().replace("-", "_")`가 하이픈만 처리하고 공백/점/숫자로 시작하는 경우를 안 거름 — `"3d app"` → `3d_app` 패키지명은 숫자로 시작해서 컴파일 불가
- Java Spring Boot: `f"{group_id}.{project_name}"`이 그대로 Initializr에 패키지명으로 전달됨 — 로컬 검증 없음

### 3. npm/Composer 패키지명 규칙 위반

`json.dumps`로 이스케이프는 되지만(인젝션은 안전), npm(`package.json`)/Composer(`composer.json`)의 이름 규칙(소문자, 특정 charset)은 검증 안 함 — 대문자/공백 있는 이름이면 `npm install`/`composer install`이 그 이유로 실패하는데 에러 메시지엔 "왜"가 안 나오고 그냥 "install failed"만 나옴.

## 영향

거의 모든 언어/프레임워크의 `stoke init`이, 사용자가 흔히 지을 법한 이름(공백/점 포함)에 대해 "성공했다"고 나온 뒤 바로 다음 명령에서 깨짐. 사용자 입장에선 원인 파악이 매우 어려움 (스캐폴딩은 성공 메시지를 냈으니까).

## 수정

진입점 두 곳(`prompts.py`의 `resolve_project_name()`, `init.py`의 `cmd_init()`/`cmd_init_noninteractive()`)에서 공통으로 쓰는 `_sanitize_project_name()`을 `prompts.py`에 추가. 영문자로 시작 + 영숫자/-/_만 허용하는 정규식(`^[A-Za-z][A-Za-z0-9_-]*$`)을 벗어나면 안전한 문자로 치환하고(`/`, `..`, 공백, 점, 따옴표 등은 전부 `-`로 치환되거나 제거됨 — 경로 traversal도 부수적으로 막힘), 사용자에게 "Note: project name sanitized to '...'" 안내를 출력함. 비대화형 모드(`cmd_init_noninteractive`, CI에서 씀)는 자동 치환 대신 명확한 에러 + 제안값을 보여주고 종료(자동으로 이름이 바뀌면 스크립트가 예상 못 한 값을 쓰게 될 수 있어서).

이 진입점 하나만 고치면 되므로 11개 프레임워크 파일은 개별 수정 안 함 — 전부 이 함수를 거쳐서 이름을 받기 때문. 부수 효과로 Kotlin Spring Boot의 "숫자로 시작하는 패키지명" 문제(`package_name = project_name.lower().replace("-", "_")`)도 project_name이 항상 영문자로 시작하도록 보장되면서 같이 해결됨.

Go의 `module_name`은 별도 프롬프트(`github.com/user/myapp` 같은 슬래시 포함 형식이 정상)라 위 함수로 못 막아서, `sanitize_go_module_name()`을 따로 추가 — 슬래시/점은 허용하되 따옴표/백슬래시/개행처럼 생성된 `main.go`의 문자열 리터럴을 깨는 문자만 걸러냄. gin/echo/fiber/chi 4개 파일에 연결.

npm/Composer 패키지명 소문자 규칙은 `express.py`/`fastify.py`/`slim.py`에서 `.lower()` 추가로 대응.
