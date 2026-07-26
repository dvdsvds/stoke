"""Go 어댑터: go build/run 위임."""
import subprocess
import shutil
from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.config import Target, ProjectInfo

class GoAdapter(BaseAdapter):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)
        self.build_dir = project_root / ".stoke" / "go" / target.name
        self.output_path = self.build_dir / (target.name + (".exe" if self._is_windows() else ""))

    @staticmethod
    def _is_windows() -> bool:
        import sys
        return sys.platform == "win32"

    def _find_go(self) -> str:
        """go 실행파일 경로 찾기."""
        go_exe = shutil.which("go")
        if go_exe is None:
            raise RuntimeError(
                "go not found in PATH.\n"
                "  Install with: stoke install --language=go --version=latest"
            )
        return go_exe

    def build(self, force: bool = False) -> None:
        """go build로 빌드."""
        go_exe = self._find_go()

        # 버전 확인
        result = subprocess.run(
            [go_exe, "version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            version_line = result.stdout.strip()
            print(f"Using {version_line}")

        # go build
        self.build_dir.mkdir(parents=True, exist_ok=True)
        print(f"Building 'go build' -> {self.output_path}")

        cmd = [
            go_exe, "build",
            "-o", str(self.output_path),
            ".",
        ]
        result = subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"go build failed:\n{result.stderr}"
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
        return [".stoke/"]