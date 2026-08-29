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
        self.csproj_path = self._find_csproj_path()
        self.assembly_name = self.csproj_path.stem if self.csproj_path else target.name
        bin_name = self.assembly_name + (".exe" if self._is_windows() else "")
        self.output_path = self.build_dir / bin_name

    @staticmethod
    def _is_windows() -> bool:
        return sys.platform == "win32"

    def _find_csproj_path(self) -> Path | None:
        """
        사용할 .csproj 경로.

        <target.name>/ 서브디렉토리에 .csproj가 있으면 그걸 씀 (멀티 타겟
        프로젝트 구조 -- 각 타겟이 자기만의 .csproj를 가진 독립된 폴더).
        없으면 프로젝트 루트에서 찾음 (기존 단일 타겟 프로젝트, 하위 호환).
        .NET은 .csproj 경로만 명시하면 솔루션(.sln) 없이도 그 프로젝트만
        정확히 빌드하므로, Go/Rust처럼 별도 등록 파일을 patch할 필요가 없음.
        """
        subdir_csproj = list((self.project_root / self.target.name).glob("*.csproj"))
        if subdir_csproj:
            return subdir_csproj[0]
        root_csproj = list(self.project_root.glob("*.csproj"))
        if root_csproj:
            return root_csproj[0]
        return None

    def _find_dotnet(self) -> str:
        """dotnet 실행파일 경로 찾기. 프로젝트 로컬 설치(.stoke/toolchains)를 PATH보다 우선."""
        exe_name = "dotnet.exe" if self._is_windows() else "dotnet"
        toolchains = self.project_root / ".stoke" / "toolchains"
        if toolchains.is_dir():
            for d in sorted(toolchains.iterdir(), reverse=True):
                if not d.is_dir() or not d.name.startswith("csharp-"):
                    continue
                local_dotnet = d / exe_name
                if local_dotnet.is_file():
                    return str(local_dotnet)

        dotnet_exe = shutil.which("dotnet")
        if dotnet_exe is None:
            raise RuntimeError(
                "dotnet not found in PATH.\n"
                "  Install .NET SDK from: https://dotnet.microsoft.com/download"
            )
        return dotnet_exe

    def build(self, force: bool = False) -> None:
        """dotnet build로 빌드."""
        if self.csproj_path is None:
            raise RuntimeError(
                f"No .csproj file found for target '{self.target.name}' "
                f"(looked in {self.project_root / self.target.name} and {self.project_root})."
            )

        dotnet_exe = self._find_dotnet()

        result = subprocess.run(
            [dotnet_exe, "--version"],
            capture_output=True,
            text=True,
            errors="replace",
        )
        if result.returncode == 0:
            print(f"Using .NET SDK {result.stdout.strip()}")

        self.build_dir.mkdir(parents=True, exist_ok=True)
        print(f"Building 'dotnet build' -> {self.output_path}")

        cmd = [
            dotnet_exe, "build",
            str(self.csproj_path),
            "--output", str(self.build_dir),
        ]
        if force:
            cmd.append("--no-incremental")
        result = subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            errors="replace",
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
