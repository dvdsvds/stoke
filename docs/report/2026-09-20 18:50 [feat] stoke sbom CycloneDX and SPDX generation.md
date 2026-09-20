# stoke sbom -- CycloneDX/SPDX SBOM 생성

- 날짜: 2026-09-20
- 종류: feat

## 배경

SBOM(Software Bill of Materials, 소프트웨어 부품 명세)은 "이 소프트웨어에 어떤 의존성이 들어있는지"를 표준 포맷으로 적어놓은 파일. 미국 행정명령 14028(공급망 보안, SolarWinds 사고 이후) 이래로 정부 조달, 금융권, 일부 대기업이 소프트웨어 납품 시 SBOM 제출을 요구하는 경우가 늘고 있고, 새 취약점이 터졌을 때("이 라이브러리 쓰는 프로젝트가 어디야?") 회사 전체 프로젝트를 검색 가능하게 만들어줌. `stoke audit`(CVE 스캔)이 쓰는 것과 거의 같은 데이터(lock 파일/네이티브 툴의 확정 버전)를 표준 파일로 출력하기만 하면 돼서 구현 비용 대비 효율이 좋다고 판단해 추가.

## SBOM 포맷 종류

업계에서 실질적으로 쓰이는 SBOM 포맷은 크게 두 가지:

- **CycloneDX** — OWASP가 만든 포맷. JSON/XML을 지원하고 스키마가 상대적으로 단순함. 보안 취약점 정보(vulnerabilities)를 SBOM 안에 직접 담는 것까지 염두에 두고 설계돼서, Dependency-Track/Grype/Trivy 같은 보안 스캐너 생태계에서 사실상 표준처럼 쓰임. 이번 구현의 기본값(`--format=cyclonedx`).
- **SPDX** (Software Package Data Exchange) — Linux Foundation이 만든 포맷, ISO/IEC 5962:2021로 국제 표준화됨. 원래 오픈소스 라이선스 컴플라이언스 추적용으로 시작해서 스키마가 더 formal하고 무거움 (JSON/YAML/RDF/tag-value 등 여러 직렬화 지원, 이번 구현은 JSON만). 미국 NTIA의 SBOM 최소 요소 기준에서 CycloneDX와 나란히 인정되는 포맷이라, 정부/컴플라이언스 요구사항에서 SPDX를 구체적으로 지정하는 경우가 있음.

둘 다 각 의존성을 **purl**(Package URL, `pkg:<ecosystem>/<name>@<version>` 형식 — 예: `pkg:pypi/requests@2.31.0`)로 식별하는 게 공통점. 실무에서는 "SBOM 하나만 내면 되는 게 아니라 상대방이 요구하는 포맷에 맞춰야" 하는 경우가 많아서 처음부터 두 포맷 다 지원하도록 설계함.

## 변경

`src/stoke/sbom.py` 신규 (언어별 의존성 수집) + `src/stoke/cli/sbom.py` 신규 (CLI + 포맷 writer):

- **Python**: `stoke.lock`의 `packages`(확정 버전) → `pkg:pypi/<정규화된 이름>@<버전>`. purl 스펙이 요구하는 PEP 503 정규화(소문자 + `-`로 치환)도 적용.
- **Java**: `stoke.lock`의 `java_deps`(`group:artifact` → 버전) → `pkg:maven/<group>/<artifact>@<버전>`.
- **Go**: `go list -m -json all` — Go 툴체인에 내장, 별도 설치 불필요. 출력이 JSON 배열이 아니라 개행 없이 이어붙은 JSON 오브젝트 여러 개라 `json.JSONDecoder.raw_decode`로 하나씩 뜯어냄. `Main: true`인 자기 자신은 제외.
- **Rust**: `cargo metadata --format-version=1` — cargo에 내장. `source`가 `null`인 패키지(워크스페이스 멤버 자신)는 제외하고 외부 registry 패키지만 수집.
- **JavaScript/TypeScript**: `npm ls --all --json`의 중첩된 `dependencies` 트리를 재귀적으로 펼쳐서 이름/버전 dedupe. 스코프 패키지(`@scope/name`)는 purl 스펙대로 `%40`으로 percent-encode.
- `stoke sbom [--target=X] [--format=cyclonedx|spdx] [--output=path|-]` — 기본은 프로젝트 루트에 `sbom.cdx.json`/`sbom.spdx.json` 파일로 씀, `--output=-`면 표준출력.

## 검증

실제 프로젝트로 전부 확인:
- Go: `stoke init -l go` 후 `go get github.com/google/uuid@v1.6.0` → CycloneDX JSON에 정확한 purl(`pkg:golang/github.com/google/uuid@v1.6.0`)로 나오는 것 확인.
- Rust: `serde` 의존성 추가 후 `cargo generate-lockfile` → SPDX 포맷으로 전이 의존성(`proc-macro2`, `quote`, `serde_core` 등)까지 전부 나오는 것 확인. (cargo metadata를 stderr와 stdout을 분리해서 호출해야 한다는 걸 테스트 중 발견 -- 합쳐서 파이프하면 "Updating crates.io index" 같은 진행 메시지가 JSON 스트림에 섞여 파싱이 깨짐.)
- JS/TS: `lodash` 설치 후 스코프 패키지(`@esbuild/linux-x64`, `@types/node`) 포함 7개 컴포넌트가 정확한 purl로 나오는 것과, `--output` 생략 시 `sbom.cdx.json` 파일로 정상 저장되는 것 확인.

## 적용 안 한 것

- C#, Ruby, PHP, Kotlin, C/C++ — `dotnet list package --format json`(SDK 버전 의존적), `bundle`/`composer`의 신뢰할 만한 JSON 의존성 목록 부재, vcpkg 연동 미비 등 이유로 이번 범위에서 제외. `stoke audit`/`stoke outdated`보다 지원 언어가 적음.
- 라이선스 정보 (`licenseConcluded`/`licenseDeclared`) — 지금은 전부 `NOASSERTION`. 각 레지스트리(PyPI/npm/crates.io 메타데이터)에서 라이선스를 끌어오는 건 다음 단계 후보.
