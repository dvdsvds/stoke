# stoke self-update

- 날짜: 2026-09-20
- 종류: feat

## 배경

"실무 트렌드를 따라가자"는 요청으로 나온 아이디어 중 하나. `rustup`/`deno`/`bun`처럼 설치된 CLI를 그 자리에서 최신 버전으로 올리는 명령. 지금까지 stoke는 릴리스 페이지에서 수동으로 다운받아 압축을 풀어야 했음.

## 배포 구조 파악

구현 전에 `stoke.spec`/`installer.iss`/`.github/workflows/release.yml`를 확인해서 실제 배포 형태를 정확히 파악함:

- PyInstaller가 `COLLECT`(onedir 모드)로 빌드 — 즉 배포물이 단일 실행 파일이 아니라 `stoke/` 폴더(실행 파일 + 번들된 Python/라이브러리 전부)임.
- Linux/macOS: `stoke-{version}-{platform}-{arch}.tar.gz`, 압축 풀면 `stoke/stoke` 실행 파일이 있는 구조.
- Windows: 별도 tarball 없이 Inno Setup 설치 프로그램(`stoke-setup-{version}.exe`)만 배포됨. `installer.iss`에 `PrivilegesRequired=lowest`, 설치 경로가 `{localappdata}\Programs\stoke`라 관리자 권한 없이 조용히(silent) 재실행 가능하다는 것도 확인.

이 구조 차이 때문에 플랫폼별로 업데이트 방식이 완전히 다름.

## 변경

`src/stoke/self_update.py` (핵심 로직) + `src/stoke/cli/self_update.py` (CLI):

- `fetch_latest()` — GitHub Releases API(`/repos/dvdsvds/stoke/releases/latest`)로 최신 버전+에셋 목록 조회.
- `is_frozen()` — PyInstaller로 빌드된 실행 파일이 아니면(`pip install -e .` 등 소스 실행) 아예 거부. 소스 실행 중엔 "업데이트할 자기 자신"이라는 개념이 없어서.
- **Linux/macOS**: 새 tarball을 임시 디렉토리에 받아서 압축 풀고(zip-slip 방지용 경로 검증 포함), 현재 설치 디렉토리를 `<dir>.old`로 rename → 새 디렉토리를 원래 자리로 이동 → 성공하면 백업 삭제. 실패하면 백업에서 롤백. 현재 실행 중인 프로세스가 자기 자신의 실행 파일을 rename/삭제해도 POSIX에서는 안전하다는 점(프로세스가 inode를 이미 열고 있어서 계속 실행됨)을 이용함.
- **Windows**: 실행 중인 `.exe`/DLL은 자기 자신이 열려있는 동안 덮어쓸 수 없어서, 설치 프로그램을 받아 `/VERYSILENT /SUPPRESSMSGBOXES /NORESTART`로 백그라운드에 분리 실행(`DETACHED_PROCESS`)해두고 우리 프로세스는 그대로 종료. 설치 프로그램이 우리가 끝난 뒤에 파일을 갈아치움.
- `stoke self-update [--check] [--yes]` — `--check`는 새 버전 여부만 확인, `--yes`는 확인 프롬프트 생략.

## 검증

실제 배포된 v2.4.0 릴리스로 end-to-end 테스트:
- `fetch_latest()`/`is_newer()`/`_platform_asset_name()` 전부 실제 GitHub API로 검증.
- **가장 중요한 테스트**: 가짜 설치 디렉토리(`stoke/stoke`에 더미 파일)를 만들어놓고 실제 v2.4.0 Linux tarball을 대상으로 `apply_update_unix()`를 직접 호출 → 디렉토리가 실제 stoke 바이너리로 통째로 교체됐고, 교체된 바이너리가 `stoke --version`으로 `2.4.0`을 정확히 출력하는 것까지 확인. 백업 디렉토리(`.old`)도 정상적으로 정리됨.
- 소스에서 실행 중(`is_frozen() == False`) 상태에서 `stoke self-update` 실행 시 명확한 에러로 거부되는 것 확인.

Windows 경로(`apply_update_windows`)는 이 환경이 Linux라 실제 실행 테스트는 못 했음 — 코드 리뷰 기준으로는 맞지만, 실제 Windows에서 한 번 검증이 필요함.

## 적용 안 한 것

- 다운로드 파일의 체크섬/서명 검증 — 지금 release workflow가 SHA256SUMS나 서명을 안 만들어서 검증할 대상이 없음. HTTPS로 공식 GitHub 릴리스에서만 받는 걸 신뢰 경계로 삼음 (README의 기존 수동 설치 안내와 동일한 신뢰 모델). 이후 "빌드 아티팩트 서명/증명(SLSA provenance)"을 하게 되면 여기서 검증하도록 연결하면 됨.
- Windows 자동화 테스트 — 위 참고.
