# zip-slip, TOML 인젝션, Linux Rust 설치 깨짐 — 3건 수정

- 날짜: 2026-09-18
- 심각도: high
- 상태: 수정됨
- 영역: `install_lang.py`(툴체인 설치), `toml_editor.py`(`stoke add`)

이전 세션에서 다루지 않은 영역(config.py, toml_editor.py, lock 파일, IDE sync, vcpkg, install_lang.py, 플러그인 시스템, http_utils, cache.py, 압축 해제 전반)을 새로 감사해서 나온 것 중 HIGH 3개.

## 1. 툴체인 설치 압축 해제에 zip-slip/tar-slip 방어 없음

`src/stoke/cli/install_lang.py`의 `_extract_zip`/`_extract_7z`/`_extract_tar`가 `extractall()`을 엔트리별 경로 검증 없이 호출함. 다운로드 URL은 `--base-url`/`STOKE_VERSION_API_BASE`로 **사용자가 바꿀 수 있게** 되어 있고(사내 미러링 용도로 의도된 기능) — 그 미러가 침해되거나 설정이 잘못되면 `../../` 같은 엔트리가 든 압축파일로 dest 밖 임의 경로에 파일을 쓸 수 있음.

**수정**: `_check_safe_members(names, dest)` 공용 헬퍼를 추가해서 압축 해제 전에 모든 엔트리 경로가 `dest.resolve()` 안에 있는지 확인. zip/7z/tar 세 군데 다 적용. (같은 클래스의 버그를 `java/frameworks/spring_boot.py`의 Initializr zip에서 이미 고친 적 있어서 같은 패턴 재사용.)

## 2. `stoke add`의 TOML 인젝션

`src/stoke/toml_editor.py`의 `add_dep()`이 `lib_name`/`version`을 이스케이프 없이 f-string으로 그대로 `stoke.toml`에 씀:

```python
content += f"\n{section_header}\n{lib_name} = \"{version}\"\n"
```

`stoke add foo '1.0" \n[evil]\nx="y'` 같은 버전 문자열을 넣으면 `stoke.toml`에 임의 섹션/키가 주입됨. 예전에 고친 "프로젝트 이름이 TOML을 깨뜨리는" 버그와 같은 계열.

**수정**: `lib_name`은 안전한 TOML bare key charset(`^[A-Za-z0-9_-]+$`)인지 검증해서 아니면 `ValueError`, `version`은 TOML basic string 규칙대로 이스케이프(`\`, `"`, 개행 등)해서 저장. `cli/deps.py`가 `ValueError`도 잡아서 깔끔한 에러로 출력하도록 수정.

## 3. `stoke install rust`가 Linux에서 항상 실패

`_install_rust()`가 다운로드한 `rustup-init`을 실행 권한 없이(`open(dest, "wb")`로 받은 파일은 보통 644) 그대로 `subprocess.run([rustup_init, ...])` 하려고 해서, Linux/macOS에서 **매번 `PermissionError`로 죽음** — chmod를 어디서도 안 했음. 기능 자체가 고장난 상태였음.

**수정**: `_install_rust()`에서 실행 전에 POSIX면 `rustup_init.chmod(rustup_init.stat().st_mode | 0o111)`로 실행 비트를 켜도록 추가.

## 검증

- 악성 zip(`../../evil.txt` 엔트리)으로 `_extract_zip` 직접 호출 → 차단됨, dest 밖에 파일 안 생김 확인
- `add_dep()`에 따옴표+개행 섞인 version 넣어서 직접 호출 → 이스케이프된 안전한 TOML로 저장됨 확인, 잘못된 패키지명은 `ValueError` 확인
- chmod 로직 직접 실행해서 644 → 755로 바뀌는 것 확인

## 변경 파일

- `src/stoke/cli/install_lang.py`
- `src/stoke/toml_editor.py`
- `src/stoke/cli/deps.py`
