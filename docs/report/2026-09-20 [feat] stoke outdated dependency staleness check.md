# stoke outdated -- 의존성 최신 버전 대비 뒤처짐 확인

- 날짜: 2026-09-20
- 종류: feat

## 배경

`stoke audit`(CVE 스캔)과는 별개 질문: "취약점은 없어도 얼마나 오래된 버전을 쓰고 있냐"는, 나중에 몰아서 마이그레이션할 때 비용이 커지는 걸 미리 보여주는 지표라 실무에서 따로 필요함. `stoke audit` 작업 때 만들어둔 인프라(언어별 위임 구조, `tool_install.toolchain_env`)를 거의 그대로 재사용.

## 변경

`src/stoke/outdated.py` 신규 (조회 로직) + `src/stoke/cli/outdated.py` 신규 (CLI):

- **Python**: `stoke.lock`의 확정 버전 → PyPI JSON API(`https://pypi.org/pypi/<name>/json`)로 최신 버전 직접 조회. 별도 도구 불필요.
- **Java**: `stoke.lock`의 확정 버전 → Maven의 `maven-metadata.xml`(`<release>` 태그)을 직접 조회. `java/maven.py`의 `get_maven_repo_url()`/`get_maven_credentials()`를 그대로 재사용해서 사내 미러 설정(`STOKE_MAVEN_REPO_URL` 등)도 자동으로 존중함.
- **JS/TS**: `npm outdated` 위임 (뒤처진 패키지 있으면 exit 1인 것도 그대로 활용).
- **C#**: `dotnet list package --outdated`.
- **PHP**: `composer outdated --direct`.
- **Go**: `go list -u -m all` — Go 툴체인에 내장, 별도 설치 불필요.
- **Rust**: `cargo outdated` (cargo-outdated 크레이트, 없으면 설치 명령 안내).
- **Ruby**: `bundle outdated` — Bundler 자체 내장 기능이라 별도 gem 불필요 (`bundler-audit`과 다름).
- **Kotlin/C/C++**: `stoke audit`와 동일한 이유로 미지원.

**리팩터**: `stoke/cli/audit.py`에 있던 `_audit_external_tool`(govulncheck/cargo-audit/bundler-audit처럼 별도 설치 필요한 툴 실행하는 공용 로직)을 `tool_install.run_with_toolchain_or_hint`로 옮겨서 audit/outdated 양쪽에서 재사용하도록 정리.

## 검증

네트워크로 실제 조회 확인: `requests` PyPI 최신 버전(`2.34.2`), `gson` Maven 최신 버전(`2.14.0`) 정상 조회. 존재하지 않는 패키지는 `None` 반환 확인. `stoke.lock`을 손으로 만들어 `stoke outdated` 전체 플로우 실행 — 뒤처진 패키지 있을 때 `exit=1`과 목록 출력, 최신일 때 `exit=0`과 "up to date" 메시지 둘 다 확인.

## 적용 안 한 것

- Kotlin/C/C++ 지원 — `stoke audit`와 동일한 이유로 범위 밖.
- 버전 비교가 단순 문자열 불일치 기준 (latest != current). semver 순서 비교까지는 안 함 — PyPI/Maven이 항상 최신을 정확히 보고한다는 전제로 충분하다고 판단.
