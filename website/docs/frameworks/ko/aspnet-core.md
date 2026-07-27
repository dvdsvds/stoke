# ASP.NET Core

ASP.NET Core 프로젝트 생성:

```bash
stoke init aspnet-core
```

minimal API 프로젝트를 생성합니다 — 컨트롤러/MVC 스캐폴딩 없는 경량 ASP.NET Core 스타일입니다.

## 프롬프트

- **Project name**: 프로젝트 디렉토리 이름

## 생성 파일

    myapp/
    ├── stoke.toml
    ├── myapp.csproj              # Microsoft.NET.Sdk.Web, dotnet 설치돼 있으면 `dotnet new web`으로 생성
    └── Program.cs                 # minimal API 진입점

## 의존성

- ASP.NET Core 공유 프레임워크 외 별도 NuGet 패키지 없음 (minimal API 템플릿 기준)

## 기본 설정

- **Port**: `5000` (`app.Run("http://localhost:5000")`로 고정 — 기본 템플릿의 HTTPS 개발 인증서 프롬프트를 피하기 위함)
- **Endpoints**:
  - `GET /` → `Hello from ASP.NET Core + stoke!`
  - `GET /hello/{name}` → `Hello, {name}!`

## 실행

```bash
cd myapp
stoke build
stoke run
```

브라우저: `http://localhost:5000/`

## 커스터마이징

- 포트 변경: `Program.cs`의 `app.Run("http://localhost:5000")` 수정
- 라우트 추가: `app.MapGet(...)` / `app.MapPost(...)` 호출 추가
- 서비스 추가: `builder.Build()` 이전에 `builder.Services.Add...()` 사용
