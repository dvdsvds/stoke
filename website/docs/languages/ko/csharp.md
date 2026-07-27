# C#

stoke는 표준 `dotnet build`와 `dotnet run` 도구를 사용해 C# 프로젝트를 지원합니다.

## 요구사항

- .NET SDK ([dotnet.microsoft.com/download](https://dotnet.microsoft.com/download))
- `stoke install --language=csharp`는 아직 지원 안 함 — .NET SDK를 직접 설치

## 설정

```toml
[project]
name = "myapp"
version = "0.1.0"

[targets.myapp]
language = "csharp"
```

이게 전부. .NET은 `.csproj` 파일과 NuGet으로 자체 의존성 관리.

## 동작 방식

- `stoke build`는 `dotnet build --output .stoke/csharp/<target>` 실행
- `stoke run`은 해당 출력 디렉토리에서 빌드된 바이너리 실행
- 어셈블리 이름은 프로젝트 루트에서 찾은 첫 번째 `*.csproj` 파일에서 가져옴
- `--force`는 `dotnet build --no-incremental`로 매핑됨

## 예시

새 C# 프로젝트 생성:

```bash
mkdir myapp
cd myapp
stoke init
```

언어 메뉴에서 `C#` 선택. stoke가:

- `stoke.toml` 생성
- `dotnet new console --name myapp` 실행 (`dotnet` 없으면 직접 작성한 `.csproj`로 대체)
- Hello World가 있는 `Program.cs` 생성

그 다음:

```bash
stoke build
stoke run
```

## 프레임워크 스캐폴딩

```bash
stoke init aspnet-core    # ASP.NET Core — minimal API 템플릿
```

자세한 내용은 [Frameworks](../../frameworks/ko/overview.md) 참조.

## 참고

- `.stoke/`와 함께 `bin/`, `obj/`(MSBuild 자체 출력/중간 파일 폴더)도 `.gitignore`에 자동 추가됨
- 현재는 프로젝트당 `.csproj` 하나만 지원 (어셈블리 이름 감지 기준)
