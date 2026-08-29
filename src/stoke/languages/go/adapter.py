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
        """go 실행파일 경로 찾기. 프로젝트 로컬 설치(.stoke/toolchains)를 PATH보다 우선."""
        exe_name = "go.exe" if self._is_windows() else "go"
        toolchains = self.project_root / ".stoke" / "toolchains"
        if toolchains.is_dir():
            for d in sorted(toolchains.iterdir(), reverse=True):
                if not d.is_dir() or not d.name.startswith("go-"):
                    continue
                local_go = d / "go" / "bin" / exe_name
                if local_go.is_file():
                    return str(local_go)

        go_exe = shutil.which("go")
        if go_exe is None:
            raise RuntimeError(
                "go not found in PATH.\n"
                "  Install with: stoke install --language=go --version=latest"
            )
        return go_exe

    def _package_path(self) -> str:
        """
        빌드할 Go 패키지 경로.

        <target.name>/ 서브디렉토리에 .go 파일이 있으면 그걸 빌드 (멀티 타겟
        구조 — go.mod 하나 밑에 cmd/api, cmd/worker처럼 여러 main 패키지를
        두는 Go의 표준 관례를 그대로 씀). 없으면 프로젝트 루트(.)를 빌드
        (기존 단일 타겟 프로젝트, 하위 호환).
        """
        target_subdir = self.project_root / self.target.name
        if target_subdir.is_dir() and list(target_subdir.glob("*.go")):
            return f"./{self.target.name}"
        return "."

    def build(self, force: bool = False) -> None:
        """go build로 빌드."""
        go_exe = self._find_go()

        # 버전 확인
        result = subprocess.run(
            [go_exe, "version"],
            capture_output=True,
            text=True,
            errors="replace",
        )
        if result.returncode == 0:
            version_line = result.stdout.strip()
            print(f"Using {version_line}")

        # go build
        self.build_dir.mkdir(parents=True, exist_ok=True)
        package_path = self._package_path()
        print(f"Building 'go build {package_path}' -> {self.output_path}")

        cmd = [
            go_exe, "build",
            "-o", str(self.output_path),
            package_path,
        ]
        result = subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            errors="replace",
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