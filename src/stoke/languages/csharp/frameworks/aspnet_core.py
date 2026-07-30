"""ASP.NET Core (C#) 프로젝트 스캐폴딩."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.prompts import _prompt, resolve_project_dir

def cmd_init_aspnet_core():
    """stoke init aspnet-core 명령어."""
    print("Creating ASP.NET Core (C#) project\n")

    project_name, project_path, is_empty = resolve_project_dir("myapp")

    _write_stoke_toml(project_path, project_name)

    dotnet_exe = shutil.which("dotnet")
    if dotnet_exe:
        print("\nScaffolding with 'dotnet new web'...")
        subprocess.run(
            [dotnet_exe, "new", "web", "--name", project_name, "--output", str(project_path), "--force"],
            capture_output=True,
        )
    else:
        print("\nWarning: 'dotnet' not found. Install .NET SDK from https://dotnet.microsoft.com/download", file=sys.stderr)
        _write_csproj(project_path / f"{project_name}.csproj")

    _write_program_cs(project_path / "Program.cs")

    print(f"\nASP.NET Core project created at: {project_path}")
    print()
    print("Next steps:")
    if not is_empty:
        print(f"  cd {project_name}")
    print(f"  stoke build")
    print(f"  stoke run")
    print()
    print("After running, open: http://localhost:5000/")

def _write_stoke_toml(project_path: Path, project_name: str) -> None:
    content = f'''[project]
name = "{project_name}"
version = "0.1.0"
lock_mode = "commit"

[targets.{project_name}]
language = "csharp"
'''
    (project_path / "stoke.toml").write_text(content, encoding="utf-8")

def _write_csproj(path: Path) -> None:
    content = '''<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

</Project>
'''
    path.write_text(content, encoding="utf-8")

def _write_program_cs(path: Path) -> None:
    content = '''var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => "Hello from ASP.NET Core + stoke!");
app.MapGet("/hello/{name}", (string name) => $"Hello, {name}!");

app.Run("http://localhost:5000");
'''
    path.write_text(content, encoding="utf-8")
