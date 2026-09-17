# ASP.NET Core / Spring Boot(Java): 실패해도 "성공"으로 끝나고 깨진 프로젝트만 남음

- 날짜: 2026-09-17
- 심각도: high
- 상태: 수정됨

## ASP.NET Core: `dotnet new web` 실패 시 `.csproj`가 아예 안 생김

`src/stoke/languages/csharp/frameworks/aspnet_core.py:17-32`:

```python
if dotnet_exe:
    print("\nScaffolding with 'dotnet new web'...")
    result = subprocess.run([dotnet_exe, "new", "web", ...], capture_output=True, text=True)
    if result.returncode != 0:
        print("\nWarning: dotnet new web failed:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
else:
    ...
    _write_csproj(project_path / f"{project_name}.csproj")

_write_program_cs(project_path / "Program.cs")
```

`dotnet`이 PATH에 있는데 `dotnet new web`이 실패하면(SDK 버전 문제, 템플릿 restore 실패, 네트워크 문제 등) — 경고만 찍고 `_write_csproj()` 폴백은 **`dotnet_exe`가 아예 없을 때만** 호출됨(else 분기). 그다음 `_write_program_cs()`는 무조건 실행됨. 결과: `Program.cs`는 있는데 **`.csproj`가 없는, 빌드/실행 불가능한 프로젝트**가 만들어지고, 함수는 `sys.exit` 없이 그대로 "project created" 성공 메시지까지 출력함.

## Java Spring Boot: 버전 조회 실패 시 폴백 버전 문자열 자체가 무효

`src/stoke/languages/java/frameworks/spring_boot.py:70`:

```python
boot_version = _prompt("Spring Boot version", "4.1.0.RELEASE")
```

Spring Initializr에서 실제 버전 목록을 못 가져왔을 때(오프라인, API 다운 등) 쓰는 이 기본값 자체가 문제:
1. Spring Boot는 2.1 이후로 `.RELEASE` 접미사를 안 씀 — `X.Y.Z.RELEASE` 형태 버전 문자열은 존재하지 않음
2. 이 값을 `bootVersion`으로 `start.spring.io`에 그대로 보내면 HTTP 400으로 거부될 가능성이 높음
3. 원래 버전 조회 메커니즘이 이미 실패한 상황에서 쓰이는 폴백인데, 그 폴백조차 깨져 있어서 **정상 경로가 하나도 없는** 최악의 케이스

## 수정

- ASP.NET Core (`aspnet_core.py`, `csharp/init.py` 둘 다): `_write_csproj()` 폴백을 else 분기 밖으로 빼서 `if not any(project_path.glob("*.csproj")): _write_csproj(...)`로 변경 — dotnet이 없을 때뿐 아니라 있었는데 실패했을 때도 최소 `.csproj`가 남도록 함. 겸사겸사 폴백 `.csproj`의 `net8.0`도 `net9.0`으로 갱신.
- Java Spring Boot: 폴백 버전 문자열을 `"4.1.0.RELEASE"` → `"3.3.5"`(`.RELEASE` 접미사 없이, 라이브 조회 결과와 같은 포맷)로 교체. 겸사겸사 `zf.extractall(dest_dir)`에 zip-slip 방어(엔트리별 경로가 `dest_dir` 밖으로 안 나가는지 확인) 추가.
