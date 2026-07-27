"""PHP 어댑터: composer/php 실행."""
import shutil
import subprocess
from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.config import Target, ProjectInfo

class PHPAdapter(BaseAdapter):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)
        self.composer_json = project_root / "composer.json"

    def _find_php(self) -> str:
        """php 실행파일 경로 찾기."""
        php_exe = shutil.which("php")
        if php_exe is None:
            raise RuntimeError(
                "php not found in PATH.\n"
                "  Install PHP from: https://www.php.net/downloads"
            )
        return php_exe

    def build(self, force: bool = False) -> None:
        """composer install (composer.json 있을 때만)."""
        php_exe = self._find_php()

        result = subprocess.run(
            [php_exe, "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Using {result.stdout.splitlines()[0].strip()}")

        if not self.composer_json.exists():
            print("No composer.json found. Skipping composer install.")
        else:
            composer_exe = shutil.which("composer")
            if composer_exe is None:
                raise RuntimeError(
                    "composer not found in PATH.\n"
                    "  Install from: https://getcomposer.org/download/"
                )
            print("Running composer install...")
            result = subprocess.run(
                [composer_exe, "install"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"composer install failed:\n{result.stderr}"
                )

        self._ensure_gitignore()
        print(f"Build complete: {self.target.name}")

    def _run_command(self) -> list[str]:
        if not self.target.entry:
            raise RuntimeError(
                f"Target '{self.target.name}' has no 'entry' field in stoke.toml."
            )
        entry_path = self.project_root / self.target.entry
        if not entry_path.exists():
            raise RuntimeError(f"Entry file not found: {entry_path}")
        return [self._find_php(), str(entry_path)]

    def run(self) -> int:
        """php entry.php 실행."""
        cmd = self._run_command()
        print(f"Running: {cmd[-1]}\n")
        try:
            result = subprocess.run(cmd, cwd=str(self.project_root))
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        """hot-reload용 실행 명령어."""
        return self._run_command()

    def _gitignore_entries(self) -> list[str]:
        return [".stoke/", "vendor/"]
