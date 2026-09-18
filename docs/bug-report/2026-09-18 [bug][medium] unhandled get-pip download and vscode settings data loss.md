# get-pip.py 다운로드 예외처리 누락 + vscode settings.json 데이터 손실

- 날짜: 2026-09-18
- 심각도: medium
- 상태: 수정됨
- 관련: [2026-09-18 [bug][high] zip-slip TOML injection and broken rust install on linux.md](<2026-09-18 [bug][high] zip-slip TOML injection and broken rust install on linux.md>) 감사에서 같이 나온 MEDIUM 2건

## 1. `install_lang.py`: get-pip.py 다운로드에 예외 처리 없음

`_bootstrap_embeddable_python()`(Windows embeddable Python용 pip 부트스트랩)이 `urllib.request.urlopen()`을 try/except 없이 호출함 — 같은 함수 안의 다른 실패 케이스(예상과 다른 embeddable 레이아웃, pip/virtualenv 설치 실패)는 전부 "Warning: ..." 찍고 우아하게 리턴하는데, 이 다운로드 하나만 예외 처리가 없어서 네트워크 문제 시 raw traceback이 남.

**수정**: `urllib.error.URLError`/`OSError`를 잡아서 다른 실패 케이스와 동일하게 경고만 찍고 `return`.

## 2. `ide/vscode.py`: 파싱 실패한 settings.json을 조용히 덮어씀

`_load_existing()`의 주석은 "파싱 실패하면 예외로 알린다"고 되어 있는데 실제 코드는 빈 dict를 반환하고 있었음. `write_project_settings()`가 이 빈 dict 위에 stoke 관리 키만 얹어서 `.vscode/settings.json`을 덮어쓰기 때문에, JSONC 스트리퍼가 처리 못하는 형식의(진짜로 문법이 깨진) settings.json이 있으면 **사용자의 기존 설정 전체가 매 `stoke build`마다 조용히 사라짐**.

그렇다고 예외를 던지게 고치면 안 됨 — 이 함수는 `stoke build`할 때마다 IDE 동기화 과정에서 호출되므로, settings.json 파싱 실패라는 부차적인 문제 때문에 **빌드 자체가 막히는** 더 나쁜 결과가 됨.

**수정**: 파싱 완전히 실패하면 원본을 `settings.json.bak`으로 백업하고 경고를 출력한 뒤 빈 dict로 진행 — 데이터는 안 잃으면서 빌드도 안 막힘.

## 검증

- get-pip.py 다운로드를 강제로 실패시켜서 Warning 메시지로 우아하게 처리되는지 확인 (코드 리뷰 + 로직 확인)
- 깨진 JSON을 `_load_existing()`에 직접 넣어서 `.bak` 파일이 생기고 원본 내용이 그대로 보존되는 것 확인

## 변경 파일

- `src/stoke/cli/install_lang.py`
- `src/stoke/ide/vscode.py`
