"""TypeScript 어댑터: tsx로 실행."""
import subprocess
import shutil
from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.config import Target, ProjectInfo

class TypeScriptAdapter(BaseAdapter):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)

    def _find_node(self) -> str:
        node = shutil.which("node")
        if node is None:
            raise RuntimeError(
                "node not found in PATH.\n"
                "  Install with: stoke install --language=nodejs --version=latest"
            )
        return node

    def _find_npm(self) -> str:
        npm = shutil.which("npm")
        if npm is None:
            raise RuntimeError("npm not found in PATH.")
        return npm

    def build(self, force: bool = False) -> None:
        """npm install (deps 설치)."""
        node_exe = self._find_node()

        result = subprocess.run(
            [node_exe, "--version"],
            capture_output=True,
            text=True,
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
                shell=True,
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
        tsx_bin = self.project_root / "node_modules" / ".bin" / "tsx"
        tsx_cmd = shutil.which("tsx")

        if tsx_bin.exists():
            cmd = [str(tsx_bin), str(entry_path)]
        elif tsx_cmd:
            cmd = [tsx_cmd, str(entry_path)]
        else:
            raise RuntimeError(
                "tsx not found. Install with:\n"
                "  npm install --save-dev tsx"
            )

        print(f"Running: {entry_path}\n")
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                shell=True,
            )
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        entry_path = self.project_root / self.target.entry
        tsx_bin = self.project_root / "node_modules" / ".bin" / "tsx"
        if tsx_bin.exists():
            return [str(tsx_bin), str(entry_path)]
        tsx_cmd = shutil.which("tsx")
        if tsx_cmd:
            return [tsx_cmd, str(entry_path)]
        raise RuntimeError("tsx not found.")

    def _ensure_gitignore(self) -> None:
        gitignore_path = self.project_root / ".gitignore"
        needed = ["node_modules/", ".stoke/", "dist/"]

        existing = ""
        if gitignore_path.exists():
            existing = gitignore_path.read_text(encoding="utf-8")

        lines = existing.splitlines()
        to_add = [e for e in needed if e not in lines]

        if to_add:
            if existing and not existing.endswith("\n"):
                existing += "\n"
            existing += "\n".join(to_add) + "\n"
            gitignore_path.write_text(existing, encoding="utf-8")
            print(f"Updated .gitignore: added {', '.join(to_add)}")