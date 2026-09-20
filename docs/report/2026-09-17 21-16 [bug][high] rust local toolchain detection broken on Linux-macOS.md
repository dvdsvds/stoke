# Rust: 로컬 툴체인 감지가 Linux/macOS에서 항상 실패함

- 날짜: 2026-09-17
- 심각도: high
- 상태: 수정됨
- 영역: 핵심 어댑터 (`stoke install`로 설치한 프로젝트별 Rust 툴체인)

## 문제

`src/stoke/languages/rust/adapter.py:63`의 `_find_local_rust_dir()`가 플랫폼 구분 없이 Windows 바이너리 이름을 하드코딩함:

```python
if d.is_dir() and d.name.startswith("rust-") and (d / "cargo" / "bin" / "cargo.exe").exists():
```

Linux/macOS에서 실제 바이너리는 확장자 없는 `cargo`인데 `.exe`를 찾으니 조건이 항상 false — `stoke install --language=rust`로 설치한 프로젝트 로컬 Rust 툴체인이 **조용히 인식되지 않고**, 시스템 `cargo`로 폴백되거나(버전이 다르면 문제) PATH에 시스템 cargo도 없으면 "cargo not found" 에러가 남.

`_find_cargo()`(80번째 줄)도 로컬 경로를 만들 때 `"cargo.exe"`를 그대로 하드코딩해서, 63번째 줄만 고쳐도 부족함 — 반환되는 경로 자체가 틀림.

비교: `go/adapter.py:34`, `csharp/adapter.py:49`는 `self._is_windows()`로 올바르게 분기함. Rust만 이 패턴을 안 따름.

## 영향

`stoke install --language=rust`로 프로젝트별 Rust 버전을 관리하는 기능이 Linux/macOS(이 툴의 주 사용 플랫폼일 가능성이 높음)에서 사실상 동작 안 함.

## 수정

`_find_local_rust_dir()`와 `_find_cargo()` 둘 다 `self._is_windows()`로 분기해서 `exe_name = "cargo.exe" if self._is_windows() else "cargo"`를 쓰도록 수정 (`go/adapter.py` 패턴과 동일).
