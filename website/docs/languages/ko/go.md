# Go

stoke는 표준 `go build`와 `go run` 도구를 사용해 Go 프로젝트를 지원합니다.

## 요구사항

- Go 1.20 이상 (권장: 1.26.5 또는 최신)
- 설치: `stoke install --language=go --version=<version>`

## 설정

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "go"
```

이게 전부. Go는 `go.mod`로 자체 의존성 관리.

## 동작 방식

- `stoke build`는 프로젝트 루트에서 `go build -o <output>` 실행
- `stoke run`은 컴파일된 바이너리 실행
- 의존성은 `go.mod`와 `go.sum`으로 Go 자체 관리

## 예시

새 Go 프로젝트 생성:

```bash
mkdir myapp
cd myapp
stoke init
```

언어 메뉴에서 `Go` 선택. stoke가:

- `stoke.toml` 생성
- `go mod init myapp` 실행
- Hello World가 있는 `main.go` 생성

그 다음:

```bash
stoke build
stoke run
```

## 프레임워크 스캐폴딩

웹 프레임워크:

```bash
stoke init gin      # Gin — 인기 있는 고성능 HTTP 프레임워크
stoke init echo     # Echo — 미니멀, 고성능
stoke init fiber    # Fiber — Express 스타일 API
stoke init chi      # Chi — 표준 라이브러리 기반 경량 라우터
```

자세한 내용은 [Frameworks](../../frameworks/ko/overview.md) 참조.

## 참고

- stoke는 `./...`이 아니라 main 패키지 (`.`)만 빌드 — `handlers/` 같은 서브패키지와의 충돌 방지
- Go 바이너리는 런타임 포함; 실행에 별도 설치 필요 없음
- 크로스 컴파일: `GOOS=linux GOARCH=amd64 stoke build` (Go 환경 변수 동작)