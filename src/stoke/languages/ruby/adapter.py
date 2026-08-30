"""Ruby 어댑터: bundler/ruby 실행."""
import shutil
import subprocess
import sys
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

    def _find_local_ruby_bin(self) -> Path | None:
        """프로젝트의 .stoke/toolchains/ruby-*/ 에서 stoke install로 받은 RubyInstaller의
        bin/ 폴더 찾기. RubyInstaller 압축을 풀면 안에 rubyinstaller-X.Y.Z-x64/ 폴더가 있음."""
        toolchains = self.project_root / ".stoke" / "toolchains"
        if not toolchains.is_dir():
            return None
        exe_name = "ruby.exe" if sys.platform == "win32" else "ruby"
        for d in sorted(toolchains.iterdir(), reverse=True):
            if not d.is_dir() or not d.name.startswith("ruby-"):
                continue
            if (d / "bin" / exe_name).is_file():
                return d / "bin"
            for nested in d.iterdir():
                if nested.is_dir() and (nested / "bin" / exe_name).is_file():
                    return nested / "bin"
        return None

    def _find_ruby(self) -> str:
        """ruby 실행파일 경로 찾기. 프로젝트 로컬 설치(.stoke/toolchains)를 PATH보다 우선."""
        local_bin = self._find_local_ruby_bin()
        if local_bin is not None:
            exe_name = "ruby.exe" if sys.platform == "win32" else "ruby"
            return str(local_bin / exe_name)

        ruby_exe = shutil.which("ruby")
        if ruby_exe is None:
            raise RuntimeError(
                "ruby not found in PATH.\n"
                "  Install Ruby from: https://www.ruby-lang.org/en/downloads/"
            )
        return ruby_exe

    def _find_bundle(self) -> str | None:
        local_bin = self._find_local_ruby_bin()
        if local_bin is not None:
            bundle_name = "bundle.bat" if sys.platform == "win32" else "bundle"
            local_bundle = local_bin / bundle_name
            if local_bundle.is_file():
                return str(local_bundle)
        return shutil.which("bundle")

    def build(self, force: bool = False) -> None:
        """bundle install (Gemfile 있을 때만)."""
        ruby_exe = self._find_ruby()

        result = subprocess.run(
            [ruby_exe, "--version"],
            capture_output=True,
            text=True,
            errors="replace",
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
                errors="replace",
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

    def test(self, verbose: bool = False) -> int:
        """spec/ 있으면 rspec, 아니면 Rakefile의 test 태스크. Bundler로 감싸져 있으면 그걸 통해 실행."""
        bundle_exe = self._find_bundle()
        use_bundle = self.gemfile.exists() and bundle_exe is not None

        spec_dir = self.project_root / "spec"
        rakefile = self.project_root / "Rakefile"

        if spec_dir.is_dir():
            cmd = [bundle_exe, "exec", "rspec"] if use_bundle else [shutil.which("rspec") or "rspec"]
        elif rakefile.is_file():
            cmd = [bundle_exe, "exec", "rake", "test"] if use_bundle else ["rake", "test"]
        else:
            raise RuntimeError(
                "No test setup found: expected a spec/ directory (RSpec) or a Rakefile with a 'test' task.\n"
                "  Add one of these, or run your test command manually."
            )
        if verbose:
            cmd.append("--verbose" if any("rspec" in part.lower() for part in cmd) else "--trace")

        print(f"Running: {' '.join(cmd)}\n")
        try:
            result = subprocess.run(cmd, cwd=str(self.project_root))
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def _gitignore_entries(self) -> list[str]:
        return [".stoke/", ".bundle/", "vendor/bundle/"]
