"""C# 어댑터: dotnet build/run 위임."""
import subprocess
import shutil
import sys
from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.config import Target, ProjectInfo

class CSharpAdapter(BaseAdapter):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)
        self.build_dir = project_root / ".stoke" / "csharp" / target.name
        self.assembly_name = self._find_assembly_name()
        bin_name = self.assembly_name + (".exe" if self._is_windows() else "")
        self.output_path = self.build_dir / bin_name

    @staticmethod
    def _is_windows() -> bool:
        return sys.platform == "win32"

    def _find_assembly_name(self) -> str:
        """프로젝트 루트의 .csproj 파일 이름으로 어셈블리 이름 추정."""
        csproj_files = list(self.project_root.glob("*.csproj"))
        if csproj_files:
            return csproj_files[0].stem
        return self.target.name

    def _find_dotnet(self) -> str:
        """dotnet 실행파일 경로 찾기."""
        dotnet_exe = shutil.which("dotnet")
        if dotnet_exe is None:
            raise RuntimeError(
                "dotnet not found in PATH.\n"
                "  Install .NET SDK from: https://dotnet.microsoft.com/download"
            )
        return dotnet_exe

    def build(self, force: bool = False) -> None:
        """dotnet build로 빌드."""
        dotnet_exe = self._find_dotnet()

        result = subprocess.run(
            [dotnet_exe, "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Using .NET SDK {result.stdout.strip()}")

        self.build_dir.mkdir(parents=True, exist_ok=True)
        print(f"Building 'dotnet build' -> {self.output_path}")

        cmd = [
            dotnet_exe, "build",
            "--output", str(self.build_dir),
        ]
        if force:
            cmd.append("--no-incremental")
        result = subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"dotnet build failed:\n{result.stdout}\n{result.stderr}"
            )

        self._ensure_gitignore()
        print(f"Build complete: {self.target.name}")

    def run(self) -> int:
        """빌드된 바이너리 실행."""
        if not self.output_path.exists():
            raise RuntimeError(
                f"Executable not found: {self.output_path}\n"
                f"  Run 'stoke build' first."
            )

        print(f"Running: {self.output_path}\n")
        try:
            result = subprocess.run([str(self.output_path)])
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        """hot-reload용 실행 명령어."""
        if not self.output_path.exists():
            raise RuntimeError(
                f"Executable not found: {self.output_path}\n"
                f"  Run 'stoke build' first."
            )
        return [str(self.output_path)]

    def _gitignore_entries(self) -> list[str]:
        return [".stoke/", "bin/", "obj/"]
