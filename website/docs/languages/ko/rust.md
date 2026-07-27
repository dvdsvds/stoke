# Rust

stoke는 표준 `cargo build`와 `cargo run` 도구를 사용해 Rust 프로젝트를 지원합니다.

## 요구사항

- Rust 툴체인 (`cargo`, `rustc`), [rustup](https://rustup.rs)으로 설치
- `stoke install --language=rust`는 아직 지원 안 함 — rustup으로 직접 설치

## 설정

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "rust"
```

이게 전부. Rust는 `Cargo.toml`로 자체 의존성 관리.

## 동작 방식

- `stoke build`는 `cargo build --release --target-dir .stoke/rust/<target>` 실행
- `stoke run`은 해당 타겟 디렉토리의 컴파일된 바이너리 실행
- 의존성은 `Cargo.toml`과 `Cargo.lock`으로 Cargo 자체 관리
- 바이너리 이름은 `Cargo.toml`의 `[package] name` 필드에서 읽음

## 예시

새 Rust 프로젝트 생성:

```bash
mkdir myapp
cd myapp
stoke init
```

언어 메뉴에서 `Rust` 선택. stoke가:

- `stoke.toml` 생성
- `cargo init --name myapp --vcs none` 실행
- Hello World가 있는 `src/main.rs` 생성

그 다음:

```bash
stoke build
stoke run
```

## 프레임워크 스캐폴딩

```bash
stoke init actix-web    # Actix-web — 성숙하고 고성능인 프레임워크
stoke init axum         # Axum — Tokio 팀이 만든 Tokio 기반 프레임워크
stoke init rocket       # Rocket — 사용 편의성 중심 프레임워크
```

자세한 내용은 [Frameworks](../../frameworks/ko/overview.md) 참조.

## 참고

- 빌드는 항상 `--release` 사용 (별도 debug 프로파일 없음)
- 재빌드 스킵 판단은 Cargo 자체 증분 캐시가 처리; `--force`는 현재 아무 동작 안 함
- `target/`(Cargo 기본 빌드 폴더, stoke는 안 씀)와 `.stoke/`가 `.gitignore`에 자동 추가됨
