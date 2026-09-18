# `go get` 이후 `go mod tidy`가 없어서 direct import가 `// indirect`로 잘못 표시됨

- 날짜: 2026-09-18
- 심각도: medium
- 상태: 수정됨 (gin/echo/fiber/chi/bubbletea 전부)

## 문제

`stoke init bubbletea`로 생성한 프로젝트에서 실제로 재현됨. 사용자가 제공한 `go.mod`:

```
require (
        github.com/aymanbagabas/go-osc52/v2 v2.0.1 // indirect
        github.com/charmbracelet/bubbletea v1.3.10 // indirect   <- main.go가 직접 import하는데도 indirect
        ...
)
```

`main.go`는 `tea "github.com/charmbracelet/bubbletea"`를 직접 import하는데도 `go.mod`에는 `// indirect`가 붙어 있었음. `// indirect`는 "메인 모듈이 직접 안 쓰고 다른 의존성이 끌고 온 것"이라는 뜻이라 이건 명백히 잘못된 표시.

원인: `go get <pkg>`는 버전 해석과 `go.mod` 갱신만 하고, "이 패키지를 로컬 소스가 실제로 direct import 하는지"를 완전히 재계산하지는 않음. 이 계산은 `go mod tidy`(또는 `go build`/`go list ./...` 같은 전체 패키지 그래프 로드)가 해줘야 함. 스캐폴딩 코드는 `main.go`를 먼저 쓴 뒤 `go get`만 실행하고 끝냈음(`src/stoke/languages/go/frameworks/bubbletea.py`) — `go mod tidy` 호출이 빠져 있었음.

## 수정 (Bubble Tea)

`cmd_init_bubbletea()`에서 `go get github.com/charmbracelet/bubbletea` 다음에 `go mod tidy` 호출을 추가. 실패 시 경고 출력도 동일하게 추가. `go` 자체가 없을 때의 수동 안내 문구에도 `go mod tidy` 줄을 추가.

## 수정 (gin, echo, fiber, chi)

`src/stoke/languages/go/frameworks/{gin,chi,echo,fiber}.py`가 전부 Bubble Tea와 똑같은 순서(`main.go` 작성 → `go mod init` → `go get <프레임워크>`)로 되어 있고 `go mod tidy` 호출이 없었음. 네 파일 모두에 `go get` 성공/실패 여부와 무관하게(어차피 go.sum 갱신을 위해) `go mod tidy` 호출을 추가하고, `go` 자체가 없을 때의 수동 안내 문구에도 `go mod tidy` 줄을 추가함. Bubble Tea와 동일한 패턴으로 통일.

실제 Go 툴체인이 로컬 환경에 없어서 `// indirect`가 사라지는지 직접 빌드해서 재현/검증은 못 했음 — Bubble Tea 케이스에서 확인된 것과 동일한 원인이므로 동일한 수정이 유효할 것으로 판단. 다음에 실제 Go 환경에서 `stoke init gin`(등)으로 생성 후 `go.mod`를 확인해서 검증 필요.
