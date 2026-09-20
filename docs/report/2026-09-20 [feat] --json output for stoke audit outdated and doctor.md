# --json 출력: stoke audit / outdated / doctor

- 날짜: 2026-09-20
- 종류: feat

## 배경

지금까지 `stoke audit`/`stoke outdated`/`stoke doctor`는 사람이 읽는 텍스트만 출력했음. CI 파이프라인이 결과를 보고 자동으로 뭔가 하게(Slack 알림, 사내 보안 대시보드, "취약점 N개 넘으면 배포 중단" 같은 게이트) 하려면 텍스트 파싱은 문구 하나만 바뀌어도 깨지기 쉬워서, 기계가 안정적으로 파싱할 수 있는 구조화된 출력이 필요함.

## 변경

세 명령 다 `--json` 플래그 추가. **완전히 구조화되는 범위와 아닌 범위가 갈림:**

- **완전 구조화**: `stoke doctor`는 애초에 모든 언어가 `CheckResult(level, message)`라는 동일한 내부 모델을 쓰기 때문에 언어에 상관없이 전부 구조화됨. `stoke audit`/`stoke outdated`의 Python/Java(OSV/PyPI/Maven 직접 조회라 stoke가 데이터를 직접 소유)와 JS/TS(`npm audit --json`/`npm outdated --json`)·PHP(`composer audit --format=json`/`composer outdated --format=json`)도 완전 구조화 — 전부 해당 도구가 이미 공식 지원하는 JSON 출력을 그대로 쓰거나(npm/composer), stoke가 직접 만든 데이터라(python/java) 가능함.
- **반쪽 구조화 (raw wrapper)**: C#(`dotnet list package`), Go(`govulncheck`), Rust(`cargo-audit`/`cargo-outdated`), Ruby(`bundler-audit`)는 각자 다른 JSON 스키마를 갖고 있거나(dotnet은 JSON 출력 자체가 SDK 버전에 따라 들쭉날쭉), 이번 세션에서 정확한 스키마를 검증할 환경이 없어서(cargo-audit/bundler-audit 등은 설치 자체가 안 돼있음), `{"structured": false, "raw_output": "..."}` 형태로 원본 텍스트를 JSON에 감싸서 반환. 최소한 "JSON 파싱은 항상 성공한다"는 보장은 유지하면서, 정직하게 "이건 파싱 안 했다"고 표시.

## 검증

실제로 여러 케이스 확인:
- `stoke doctor --json`: 유효한 JSON, `checks`/`error_count`/`warning_count` 필드 확인.
- `stoke audit --json`/`stoke outdated --json` (Python, 가짜 lock으로): `requests==2.25.0`에 대해 실제 OSV 취약점 8개, 최신 버전(`2.34.2`)까지 정확히 JSON으로 나옴. exit code도 텍스트 모드와 동일하게 동작(취약점/뒤처짐 있으면 1).
- `stoke audit --json`/`stoke outdated --json` (JS/TS, 실제 npm 프로젝트): `npm audit --json`/`npm outdated --json` 그대로 통과시켜서 유효한 JSON 확인.
- 테스트 중 `2>&1`로 stderr/stdout을 합쳐서 확인하다가 "JSON이 경고 메시지랑 섞여서 깨진다"고 착각했는데, 실제로는 `npm_check.py`의 경고가 이미 `file=sys.stderr`로 제대로 분리돼 있었음 — stdout만 따로 보면 JSON이 깨끗하다는 걸 재확인. (테스트 방법의 착오였지, 코드 버그는 아니었음.)

## 적용 안 한 것

- C#/Go/Rust/Ruby용 완전 구조화 JSON — 각 도구의 정확한 JSON 스키마를 실제로 설치해서 검증한 뒤 다음 단계로 미룸. 지금은 `raw_output`으로 감싸서 최소한 JSON 파싱 자체는 항상 되게만 해둠.
- `stoke build`/`stoke test`의 `--json` — 이번엔 "진단/리포트" 성격이 강한 audit/outdated/doctor 세 개만. build/test는 로그가 원래 길고 구조화 가치가 상대적으로 낮다고 판단해 범위에서 제외.
