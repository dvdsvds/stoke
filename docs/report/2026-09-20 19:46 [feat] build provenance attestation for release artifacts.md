# 릴리스 아티팩트 빌드 증명 (build provenance attestation)

- 날짜: 2026-09-20
- 종류: feat

## 배경

"실무 트렌드를 따라가자"의 세 번째 항목: 공급망 보안(supply chain security) 트렌드. SolarWinds 사고 이후 업계 표준처럼 자리잡은 개념으로, "이 바이너리가 진짜 이 소스코드에서, 이 CI 워크플로우로 빌드됐다"를 암호학적으로 증명하는 것. 이번 세션에서 만든 `stoke sbom`/`stoke audit`이 "이 프로젝트가 뭘 쓰는지"를 증명한다면, 이건 "이 배포 파일 자체가 진짜인지"를 증명하는 세트.

## 방식 선택

SLSA 공급망 보안 프레임워크를 구현하는 방법이 몇 가지 있는데:
1. `slsa-framework/slsa-github-generator` 재사용 워크플로우 — SLSA Level 3까지 지원하지만 설정이 복잡하고 별도 리포 구조를 요구함.
2. **GitHub 네이티브 Artifact Attestations** (`actions/attest-build-provenance`) — 2024년 GA된 GitHub 자체 기능. in-toto 증명을 만들어서 저장소의 attestation API에 등록, `gh attestation verify`로 검증. 설정이 워크플로우에 스텝 하나 추가하는 수준으로 간단함.

퍼블릭 저장소(dvdsvds/stoke)라 별도 설정 없이 2번이 바로 되고, 관리 부담이 훨씬 낮아서 이걸 선택함.

## 변경

`.github/workflows/release.yml`:

- 최상위 `permissions`에 `id-token: write`(OIDC 토큰 발급용), `attestations: write`(증명 등록용) 추가.
- `windows-installer` 잡: Inno Setup으로 인스톨러 빌드한 직후, 업로드 전에 `actions/attest-build-provenance@v2`로 `stoke-setup-{version}.exe` 증명.
- `unix-tarball` 잡(macOS/Linux 매트릭스): tarball 패키징 직후, 업로드 전에 동일하게 증명.

README.md/README_ko.md에 "다운로드 검증(선택)" 섹션 추가 — `gh attestation verify <file> --owner dvdsvds`로 사용자가 직접 검증하는 방법 안내.

## 검증

로컬에서 테스트할 수 없는 변경이라(실제 GitHub Actions OIDC + attestation API 호출이 필요), v2.4.1 패치 릴리스를 실제로 잘라서 검증함:
- 버전을 2.4.1로 올리고 태그 push → 3개 플랫폼 빌드가 attestation 스텝 포함해서 전부 성공.
- `gh attestation verify`로 Windows/macOS/Linux 아티팩트 3개 전부 검증 성공 확인 (아래 실제 출력 참고).

## 적용 안 한 것

- SLSA Level 3 재사용 워크플로우로의 전환 — 네이티브 attestation이 지금 필요보다 충분해서 보류. 나중에 더 엄격한 요구사항(정부 조달 등)이 생기면 재검토.
- 다운로드한 아티팩트를 `stoke self-update`가 자동으로 검증하는 기능 — `gh` CLI가 없는 환경도 있어서, 지금은 사용자가 원하면 수동으로 `gh attestation verify`를 돌리는 방식으로 남겨둠. `gh` 없이도 되는 검증(cosign 등)으로 self-update에 내장하는 건 다음 단계 후보.
