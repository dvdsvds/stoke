"""C# 프로젝트 초기화 로직."""
import json
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt

def _select_csharp_version() -> str:
    """
    선택적 .NET SDK 버전 pin.
    빈 입력이면 pin 안 함 (팀원마다 로컬 SDK 버전이 달라도 됨).
    """
    return _prompt(
        "Pin .NET SDK version? (e.g. 8.0.100, blank to skip)", default=""
    ).strip()

def _write_global_json(project_root: Path, version: str) -> None:
    """
    global.json 생성. dotnet CLI가 이 파일을 자동으로 읽어서
    지정된 SDK 버전이 없으면 빌드를 실패시킴.
    version이 빈 문자열이면 아무것도 안 함.
    """
    if not version:
        return
    data = {"sdk": {"version": version}}
    (project_root / "global.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )

def _write_stoke_toml_csharp(
    path: Path,
    project_name: str,
    lock_mode: str,
) -> None:
    """C# 프로젝트용 stoke.toml 쓰기."""
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "{lock_mode}"

[targets.{project_name}]
language = "csharp"
'''
    path.write_text(content, encoding="utf-8")

def _write_example_csharp(project_root: Path, project_name: str) -> None:
    """C# 예시 파일 생성 + .csproj 초기화."""
    dotnet_exe = shutil.which("dotnet")
    if dotnet_exe:
        subprocess.run(
            [dotnet_exe, "new", "console", "--name", project_name, "--output", str(project_root), "--force"],
            cwd=str(project_root),
            capture_output=True,
        )
    else:
        _write_csproj(project_root / f"{project_name}.csproj")

    program_cs = project_root / "Program.cs"
    program_cs.write_text(
        'Console.WriteLine("Hello from stoke!");\n',
        encoding="utf-8",
    )

def _write_example_csharp_subdir(target_root: Path, target_name: str) -> None:
    """
    <target_name>/ 서브디렉토리에 독립된 C# 프로젝트 생성.
    dotnet build는 .csproj 경로만 명시하면 그 프로젝트만 정확히 빌드하므로,
    Rust의 워크스페이스 members나 Kotlin의 settings.gradle.kts include()처럼
    "이 디렉토리도 프로젝트의 일부다"라고 등록해줄 필요는 없음. 다만 루트
    프로젝트 쪽은 별도로 exclude 처리가 필요함 (아래 _exclude_subdir_from_root_csproj 참고).
    """
    target_root.mkdir(parents=True, exist_ok=True)

    dotnet_exe = shutil.which("dotnet")
    if dotnet_exe:
        subprocess.run(
            [dotnet_exe, "new", "console", "--name", target_name, "--output", str(target_root), "--force"],
            cwd=str(target_root),
            capture_output=True,
        )
    else:
        _write_csproj(target_root / f"{target_name}.csproj")

    program_cs = target_root / "Program.cs"
    program_cs.write_text(
        f'Console.WriteLine("Hello from {target_name}!");\n',
        encoding="utf-8",
    )

def _exclude_subdir_from_root_csproj(project_root: Path, target_name: str) -> None:
    """
    프로젝트 루트에 있는 기존 .csproj(첫 타겟용)가 새로 추가되는 <target_name>/
    서브디렉토리를 자기 컴파일 대상에 끌어들이지 않도록 제외 규칙을 추가.

    SDK 스타일 .csproj는 기본적으로 자기 디렉토리 밑의 모든 *.cs 파일을 재귀적으로
    (bin/obj 제외) 컴파일 대상에 포함함. 그래서 새 타겟 서브디렉토리를 만들면 루트
    프로젝트가 그 파일들까지 같이 컴파일하려다가 "One compilation unit can only
    have top-level statements" 같은 충돌 에러가 남 -- 실제로 재현/확인된 문제.
    루트 .csproj가 없으면(=이 프로젝트의 첫 타겟이 서브디렉토리 구조였던 경우) 아무것도 안 함.
    """
    root_csproj_candidates = list(project_root.glob("*.csproj"))
    if not root_csproj_candidates:
        return
    root_csproj = root_csproj_candidates[0]

    remove_glob = f"{target_name}/**"
    text = root_csproj.read_text(encoding="utf-8")
    if remove_glob in text:
        return

    exclude_block = f'  <ItemGroup>\n    <Compile Remove="{remove_glob}" />\n  </ItemGroup>\n'
    if "</Project>" in text:
        text = text.replace("</Project>", exclude_block + "</Project>")
    else:
        text += exclude_block
    root_csproj.write_text(text, encoding="utf-8")

def _remove_csproj_exclude(project_root: Path, target_name: str) -> None:
    """루트 .csproj에서 <target_name>/** 제외 규칙 제거. _exclude_subdir_from_root_csproj()의 반대."""
    root_csproj_candidates = list(project_root.glob("*.csproj"))
    if not root_csproj_candidates:
        return
    root_csproj = root_csproj_candidates[0]

    remove_glob = f"{target_name}/**"
    exclude_block = f'  <ItemGroup>\n    <Compile Remove="{remove_glob}" />\n  </ItemGroup>\n'
    text = root_csproj.read_text(encoding="utf-8")
    if exclude_block not in text:
        return
    text = text.replace(exclude_block, "")
    root_csproj.write_text(text, encoding="utf-8")

def _write_csproj(path: Path) -> None:
    content = '''<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

</Project>
'''
    path.write_text(content, encoding="utf-8")
