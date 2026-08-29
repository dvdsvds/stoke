# 설치

stoke는 Windows, Linux, macOS에서 사용할 수 있습니다. 플랫폼을 선택하세요:

## Windows

### 방법 1: Windows 인스톨러 (권장)

[GitHub Releases](https://github.com/dvdsvds/stoke/releases/latest)에서 최신 인스톨러를 다운로드하세요:

- 파일: `stoke-setup-X.Y.Z.exe`
- 설치 위치: `%LOCALAPPDATA%\Programs\stoke`
- **사전 준비 필요 없음** — Python이 인스톨러에 번들로 포함됨
- 관리자 권한 불필요
- 설치 중 PATH 추가 옵션 제공

설치 후 확인:

```bash
stoke --version
```

## Linux / macOS

[GitHub Releases](https://github.com/dvdsvds/stoke/releases/latest)에서 플랫폼에 맞는 타볼을 다운로드하세요:

- 파일: `stoke-X.Y.Z-macos-<arch>.tar.gz` 또는 `stoke-X.Y.Z-linux-<arch>.tar.gz`
- **사전 준비 필요 없음** — Python이 바이너리에 번들로 포함됨

압축을 풀고 `PATH`에 추가하세요:

```bash
tar xzf stoke-*.tar.gz
export PATH="$PWD/stoke:$PATH"   # 셸 프로필에 추가하면 계속 유지됨
```

코드 서명은 안 되어 있습니다: macOS에서는 Gatekeeper가 첫 실행을 막습니다. `stoke` 바이너리를 우클릭(또는 Ctrl+클릭)해서 "열기"를 선택하고 한 번 확인해주세요 — 처음 한 번만 필요합니다.

## 설치 확인

```bash
stoke --version
```

설치된 버전이 출력되어야 합니다.

## 요구 사항

**stoke 자체**: 사전 준비 필요 없음 — 모든 인스톨러/타볼에 Python이 번들로 포함되어 있습니다.

**언어 툴체인** (`stoke install --language=X`로 자동 설치 가능):
- **Python 프로젝트**: Python 3.8 이상 (stoke가 감지할 수 있는 모든 버전)
- **Java 프로젝트**: JDK 17 이상 (Adoptium/OpenJDK/Zulu 권장)
- **C/C++ 프로젝트**: gcc, g++, 또는 clang
- **C/C++ 라이브러리**: vcpkg (`stoke install vcpkg`로 자동 설치 가능)

## 설치된 툴체인 확인

설치 후, stoke가 빌드할 수 있는 언어를 확인하세요:

```bash
stoke python list      # 감지된 Python 설치 목록
stoke java list        # 감지된 JDK 목록
stoke c list           # 감지된 C 컴파일러 목록
stoke cpp list          # 감지된 C++ 컴파일러 목록
```

## 다음 단계

- [빠른 시작](quick-start.md) — 첫 프로젝트 빌드하기
- [설정](../configuration/stoke-toml.md) — `stoke.toml` 레퍼런스
