"""TypeScript 어댑터: tsx로 실행."""
import sys
import subprocess
import shutil
from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.config import Target, ProjectInfo
from stoke.languages._node_tools import NodeToolsMixin

def _resolve_tsx_cmd(entry_path: Path, project_root: Path) -> list[str]:
    tsx_bin = project_root / "node_modules" / ".bin" / "tsx"
    if tsx_bin.exists():
        return [str(tsx_bin), str(entry_path)]
    tsx_cmd = shutil.which("tsx")
    if tsx_cmd:
        return [tsx_cmd, str(entry_path)]
    raise RuntimeError("tsx not found. Install with:\n  npm install --save-dev tsx")

class TypeScriptAdapter(BaseAdapter, NodeToolsMixin):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)

    def build(self, force: bool = False) -> None:
        """npm install (deps 설치)."""
        node_exe = self._find_node()

        result = subprocess.run(
            [node_exe, "--version"],
            capture_output=True,
            text=True,
            errors="replace",
        )
        if result.returncode == 0:
            print(f"Using Node.js {result.stdout.strip()}")

        package_json = self.project_root / "package.json"
        if not package_json.exists():
            print("No package.json found. Skipping npm install.")
        else:
            npm_exe = self._find_npm()
            print("Running npm install...")
            result = subprocess.run(
                [npm_exe, "install"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                errors="replace",
                shell=(sys.platform == "win32"),
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"npm install failed:\n{result.stderr}"
                )

        self._ensure_gitignore()
        print(f"Build complete: {self.target.name}")

    def run(self) -> int:
        """tsx로 TypeScript 파일 실행."""
        if not self.target.entry:
            raise RuntimeError(
                f"Target '{self.target.name}' has no 'entry' field in stoke.toml."
            )

        entry_path = self.project_root / self.target.entry
        if not entry_path.exists():
            raise RuntimeError(f"Entry file not found: {entry_path}")

        # tsx (local or global) 실행
        node_exe = self._find_node()
        cmd = _resolve_tsx_cmd(entry_path, self.project_root)

        print(f"Running: {entry_path}\n")
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                shell=(sys.platform == "win32"),
            )
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        entry_path = self.project_root / self.target.entry
        return _resolve_tsx_cmd(entry_path, self.project_root)

    def _gitignore_entries(self) -> list[str]:
        return ["node_modules/", ".stoke/", "dist/"]