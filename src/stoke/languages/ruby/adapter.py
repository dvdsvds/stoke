"""Ruby 어댑터: bundler/ruby 실행."""
import shutil
import subprocess
from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.config import Target, ProjectInfo

class RubyAdapter(BaseAdapter):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)
        self.gemfile = project_root / "Gemfile"

    def _find_ruby(self) -> str:
        """ruby 실행파일 경로 찾기."""
        ruby_exe = shutil.which("ruby")
        if ruby_exe is None:
            raise RuntimeError(
                "ruby not found in PATH.\n"
                "  Install Ruby from: https://www.ruby-lang.org/en/downloads/"
            )
        return ruby_exe

    def _find_bundle(self) -> str | None:
        return shutil.which("bundle")

    def build(self, force: bool = False) -> None:
        """bundle install (Gemfile 있을 때만)."""
        ruby_exe = self._find_ruby()

        result = subprocess.run(
            [ruby_exe, "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"Using {result.stdout.strip()}")

        if not self.gemfile.exists():
            print("No Gemfile found. Skipping bundle install.")
        else:
            bundle_exe = self._find_bundle()
            if bundle_exe is None:
                raise RuntimeError(
                    "bundler not found in PATH.\n"
                    "  Install with: gem install bundler"
                )
            print("Running bundle install...")
            result = subprocess.run(
                [bundle_exe, "install"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"bundle install failed:\n{result.stderr}"
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

        bundle_exe = self._find_bundle()
        if self.gemfile.exists() and bundle_exe:
            return [bundle_exe, "exec", "ruby", str(entry_path)]
        return [self._find_ruby(), str(entry_path)]

    def run(self) -> int:
        """ruby entry.rb 실행."""
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
        return [".stoke/", ".bundle/", "vendor/bundle/"]
