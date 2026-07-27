"""C# 프로젝트 초기화 로직."""
import subprocess
import shutil
from pathlib import Path

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
