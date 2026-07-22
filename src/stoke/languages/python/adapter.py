import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass

from stoke.adapters.base import BaseAdapter
from stoke.cache import (
    BuildCache,
    load_cache,
    save_cache,
    get_file_stat,
    is_unchanged,
)
from stoke.config import Target, ProjectInfo
from stoke.lock import LockFile, load_lock, save_lock, is_compatible
from stoke.languages.python.versions import (
    PythonInstall,
    detect_all,
    find_matching,
    _get_version,
)

@dataclass
class SyntaxCheckResult:
    file: Path
    ok: bool
    error: str = ""

class PythonAdapter(BaseAdapter):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)
        self.lang_dir = project_root / ".stoke" / "python" / target.name
        # env_type에 따라 폴더 이름 다름
        self.env_type = target.env_type
        if self.env_type == "conda":
            self.venv_dir = self.lang_dir / "conda_env"
        else:
            self.venv_dir = self.lang_dir / "venv"

    def resolve_python(self) -> tuple[PythonInstall, bool]:
        """
        어떤 파이썬을 쓸지 결정.
        반환: (PythonInstall, lock을 갱신해야 하는지 여부)
        """
        lock = load_lock(self.project_root, self.project.lock_mode)

        # 1. lock 파일 있으면 우선 사용
        if lock is not None:
            # stoke.toml에서 요청한 버전이랑 호환되는지 확인
            if self.target.python_version:
                if not is_compatible(lock.python.version, self.target.python_version):
                    print(
                        f"stoke.toml requests Python {self.target.python_version} "
                        f"but lock file has {lock.python.version}. Updating lock."
                    )
                    return self._resolve_from_stoke_toml(), True

            install = find_matching(lock.python.version)
            if install is None:
                available = detect_all()
                available_versions = ", ".join(i.version for i in available)
                raise RuntimeError(
                    f"Lock file requires Python {lock.python.version}, but it's not installed on this system.\n"
                    f"  Available versions: {available_versions}\n"
                    f"  Options:\n"
                    f"    1. Install Python {lock.python.version} on this system\n"
                    f"    2. Delete the lock file (stoke.lock or .stoke/lock.toml) to regenerate\n"
                    f"    3. Change python_version in stoke.toml to a compatible version"
                )
            return install, False

        # 2. lock 없으면 stoke.toml 기준으로 결정하고 lock 생성 예정
        return self._resolve_from_stoke_toml(), True

    def _resolve_from_stoke_toml(self) -> PythonInstall:
        """stoke.toml 기준으로 파이썬 결정 (lock 무시)."""
        if self.target.python_version:
            install = find_matching(self.target.python_version)
            if install is None:
                available = detect_all()
                available_versions = ", ".join(i.version for i in available)
                raise RuntimeError(
                    f"Python {self.target.python_version} not found on this system.\n"
                    f"  Available versions: {available_versions}\n"
                    f"  Install Python {self.target.python_version} or update python_version in stoke.toml."
                )
            return install

        # stoke.toml에도 없으면 셸 default
        installs = detect_all()
        if not installs:
            raise RuntimeError("No Python installation detected on this system")

        for install in installs:
            if install.is_default:
                return install
        return installs[0]

    def venv_python_exe(self) -> Path:
        # conda: 환경 루트에 python.exe (Windows) 또는 bin/python (Unix)
        # venv: Scripts/python.exe (Windows) 또는 bin/python (Unix)
        if sys.platform == "win32":
            exe_name = "python.exe"
            if self.env_type == "conda":
                # Conda: 환경 루트에 python.exe
                return self.venv_dir / exe_name
            else:
                # venv: Scripts/ 우선, 없으면 bin/
                scripts_path = self.venv_dir / "Scripts" / exe_name
                bin_path = self.venv_dir / "bin" / exe_name
                if scripts_path.exists():
                    return scripts_path
                if bin_path.exists():
                    return bin_path
                return scripts_path
        else:
            return self.venv_dir / "bin" / "python"

    def venv_pip_exe(self) -> Path:
        """venv/conda env 안의 pip 실행파일 경로."""
        if sys.platform == "win32":
            exe_name = "pip.exe"
            if self.env_type == "conda":
                # Conda: Scripts/pip.exe
                return self.venv_dir / "Scripts" / exe_name
            else:
                # venv: Scripts/ 우선, 없으면 bin/
                scripts_path = self.venv_dir / "Scripts" / exe_name
                bin_path = self.venv_dir / "bin" / exe_name
                if scripts_path.exists():
                    return scripts_path
                if bin_path.exists():
                    return bin_path
                return scripts_path
        else:
            return self.venv_dir / "bin" / "pip"

    def install_deps(
        self,
        lock: LockFile | None,
        force: bool = False,
    ) -> tuple[dict[str, str], bool]:
        """
        의존성 설치. 반환: (설치된 패키지 dict, 실제로 설치를 수행했는지 여부).

        - force=True면 무조건 재설치
        - lock 파일에 패키지 정보 있으면 그 정확한 버전으로 설치
        - 없으면 stoke.toml의 명세로 설치 후 실제 설치된 버전 기록
        - venv에 이미 설치된 패키지가 lock과 완전히 같으면 skip
        """
        if not self.target.deps:
            if self.verbose:
                print("No dependencies to install")
            return {}, False

        pip_exe = self.venv_pip_exe()
        if not pip_exe.exists():
            raise RuntimeError(
                f"pip not found in venv: {pip_exe}\n"
                f"  The venv may be corrupted.\n"
                f"  Try: stoke clean && stoke build"
            )

        # skip 판단: force가 아니고, lock에 패키지 정보 있고, 현재 설치 상태가 lock과 같으면
        if not force and lock and lock.packages:
            current_packages = self._pip_freeze()
            if current_packages == lock.packages:
                print(f"Dependencies up to date ({len(current_packages)} package(s))")
                return current_packages, False

        # 설치할 패키지 명세 결정
        if lock and lock.packages:
            install_args = []
            for name, version in lock.packages.items():
                install_args.append(f"{name}=={version}")
            print(f"Installing {len(install_args)} package(s) from lock file...")
        else:
            install_args = []
            for name, spec in self.target.deps.items():
                if spec and spec[0].isdigit():
                    install_args.append(f"{name}=={spec}")
                else:
                    if spec == "*" or not spec:
                        install_args.append(name)
                    else:
                        install_args.append(f"{name}{spec}")
            print(f"Installing {len(install_args)} package(s) from stoke.toml...")

        cmd = [str(pip_exe), "install", "--disable-pip-version-check"] + install_args

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(
                f"pip install failed:\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

        return self._pip_freeze(), True

    def _pip_freeze(self) -> dict[str, str]:
        """venv의 pip freeze 결과를 dict로 반환."""
        pip_exe = self.venv_pip_exe()
        result = subprocess.run(
            [str(pip_exe), "freeze", "--disable-pip-version-check"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"pip freeze failed: {result.stderr}")

        packages = {}
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # "requests==2.31.0" 형식만 처리
            # editable install(-e ...), git URL 등은 무시
            if "==" not in line:
                continue
            name, version = line.split("==", 1)
            packages[name.strip()] = version.strip()

        return packages

    def collect_source_files(self) -> list[Path]:
        """sources 패턴들을 실제 파일 목록으로 확장."""
        collected = []
        seen = set()  # 중복 제거

        for pattern in self.target.sources:
            # 패턴이 절대 경로면 그대로, 상대면 project_root 기준
            matched = list(self.project_root.glob(pattern))
            for path in matched:
                if not path.is_file():
                    continue
                if path.suffix != ".py":
                    continue
                # venv 안의 파일은 제외
                try:
                    path.relative_to(self.venv_dir)
                    continue  # venv 안에 있으면 skip
                except ValueError:
                    pass  # venv 밖이면 OK
                # .stoke 폴더 자체 제외
                try:
                    path.relative_to(self.project_root / ".stoke")
                    continue
                except ValueError:
                    pass

                real = path.resolve()
                if real in seen:
                    continue
                seen.add(real)
                collected.append(path)

        return sorted(collected)

    def check_syntax(
        self,
        files: list[Path],
        cache: BuildCache,
        force: bool = False,
    ) -> tuple[list[SyntaxCheckResult], list[Path]]:
        """
        각 파일의 문법을 체크.
        캐시에 있고 mtime/size가 같으면 skip.

        반환: (모든 결과 리스트, skip된 파일 경로 리스트)
        """
        results = []
        skipped_files = []
        venv_python = self.venv_python_exe()

        if not venv_python.exists():
            raise RuntimeError(f"venv python not found: {venv_python}")

        target_cache = cache.get_target(self.target.name)

        for file in files:
            file_key = str(file.relative_to(self.project_root))
            current_stat = get_file_stat(file)

            # 캐시에 있고 안 바뀌었으면 skip
            if not force:
                cached_stat = target_cache.syntax_check.get(file_key)
                if cached_stat is not None and is_unchanged(current_stat, cached_stat):
                    results.append(SyntaxCheckResult(file=file, ok=True))
                    skipped_files.append(file)
                    continue

            result = subprocess.run(
                [str(venv_python), "-m", "py_compile", str(file)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                results.append(SyntaxCheckResult(file=file, ok=True))
                target_cache.syntax_check[file_key] = current_stat
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                results.append(SyntaxCheckResult(
                    file=file,
                    ok=False,
                    error=error_msg,
                ))
                target_cache.syntax_check.pop(file_key, None)

        return results, skipped_files
    
    def venv_exists(self) -> bool:
        return self.venv_python_exe().exists()

    def get_venv_python_version(self) -> str | None:
        exe = self.venv_python_exe()
        if not exe.exists():
            return None
        return _get_version(str(exe))

    def create_venv(self, python: PythonInstall) -> None:
        self.venv_dir.parent.mkdir(parents=True, exist_ok=True)

        if self.env_type == "conda":
            self._create_conda_env(python)
            return

        print(f"Creating venv at {self.venv_dir}")
        print(f"  Using Python {python.version} ({python.executable})")
        # 1. venv 생성
        result = subprocess.run(
            [str(python.executable), "-m", "venv", str(self.venv_dir)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"venv creation failed:\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

        # 2. pip이 설치 안 됐으면 ensurepip으로 강제 설치
        # MSYS2/MinGW 파이썬 등 일부 배포판은 자동으로 안 됨
        pip_exe = self.venv_pip_exe()
        if not pip_exe.exists():
            venv_python = self.venv_python_exe()
            result = subprocess.run(
                [str(venv_python), "-m", "ensurepip", "--default-pip"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"Failed to install pip in venv:\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}\n"
                    f"The Python distribution at {python.executable} may not support venv properly.\n"
                    f"Try specifying a different python_version in stoke.toml."
                )

    def _create_conda_env(self, python: PythonInstall) -> None:
        """conda 환경 생성."""
        import shutil

        # conda 명령어 찾기
        conda_exe = shutil.which("conda")
        if conda_exe is None:
            raise RuntimeError(
                "conda not found in PATH.\n"
                "Install conda with: stoke install --language=conda --version=miniconda"
            )

        # 파이썬 버전 결정 (예: 3.12)
        py_ver = self.target.python_version or "3.12"
        # major.minor만 (conda가 patch까지는 필요 없음)
        py_ver_parts = py_ver.split(".")
        if len(py_ver_parts) >= 2:
            py_ver = f"{py_ver_parts[0]}.{py_ver_parts[1]}"

        print(f"Creating conda env at {self.venv_dir}")
        print(f"  Using Python {py_ver}")

        # conda create --prefix (경로 지정) --yes python=3.12
        result = subprocess.run(
            [conda_exe, "create", "--prefix", str(self.venv_dir),
             "--yes", f"python={py_ver}"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"conda env creation failed:\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

    def _ensure_gitignore(self) -> None:
        """
        lock_mode에 따라 .gitignore를 자동 관리.
        - commit: .stoke/만 무시
        - local: .stoke/ 무시 (lock 파일도 여기 있으니 자동 처리)
        """
        gitignore_path = self.project_root / ".gitignore"

        needed_entries = [".stoke/"]

        existing = ""
        if gitignore_path.exists():
            existing = gitignore_path.read_text(encoding="utf-8")

        existing_lines = set(
            line.strip() for line in existing.splitlines() if line.strip()
        )

        added = []
        for entry in needed_entries:
            if entry not in existing_lines:
                added.append(entry)

        if added:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                if existing:
                    f.write("\n# Added by stoke\n")
                else:
                    f.write("# Added by stoke\n")
                for entry in added:
                    f.write(f"{entry}\n")
            print(f"Updated .gitignore: added {', '.join(added)}")

    def build(self, force: bool = False) -> None:
        python, should_update_lock = self.resolve_python()
        lock = load_lock(self.project_root, self.project.lock_mode)
        cache = load_cache(self.project_root)
        # venv가 있는데 버전이 안 맞으면 재생성
        if self.venv_exists():
            existing_version = self.get_venv_python_version()
            if existing_version != python.version:
                print(
                    f"Existing venv has Python {existing_version}, "
                    f"but {python.version} is required. Recreating venv."
                )
                if self.env_type == "conda":
                    # conda env 제거
                    import shutil as _shutil2
                    conda_exe = _shutil2.which("conda")
                    if conda_exe:
                        subprocess.run(
                            [conda_exe, "env", "remove", "--prefix", str(self.venv_dir), "--yes"],
                            capture_output=True, text=True,
                        )
                    # 폴더도 삭제 (혹시 남아있으면)
                    if self.venv_dir.exists():
                        _shutil2.rmtree(self.venv_dir)
                else:
                    import shutil
                    shutil.rmtree(self.venv_dir)
                self.create_venv(python)
                env_label = "conda env" if self.env_type == "conda" else "venv"
                print(f"{env_label} recreated successfully")
                # venv 재생성했으니 패키지도 다시 설치해야 함
                should_update_lock = True
            else:
                print(f"Using Python {existing_version}")
                if self.verbose:
                    print(f"  venv: {self.venv_dir}")
        else:
            self.create_venv(python)
            env_label = "conda env" if self.env_type == "conda" else "venv"
            print(f"{env_label} created successfully")
        # 의존성 설치
        if self.verbose:
            print("\n--- Installing dependencies ---")
        installed_packages, deps_installed = self.install_deps(lock, force=force)
        if deps_installed:
            print(f"Installed {len(installed_packages)} package(s):")
            for name, ver in sorted(installed_packages.items()):
                print(f"  {name}=={ver}")
        # lock 파일 저장 (실제 변경 있을 때만)
        lock_path, lock_changed = save_lock(
            self.project_root,
            self.project.lock_mode,
            python.version,
            str(python.executable),
            packages=installed_packages,
        )
        if lock_changed:
            print(f"Lock file saved: {lock_path}")
        # 문법 체크
        if self.verbose:
            print("\n--- Checking syntax ---")
        source_files = self.collect_source_files()
        if not source_files:
            print("No source files found matching sources patterns")
        else:
            if self.verbose:
                print(f"Checking {len(source_files)} file(s)...")
            results, skipped_files = self.check_syntax(source_files, cache, force=force)
            skipped_set = set(skipped_files)

            failed = [r for r in results if not r.ok]
            passed = [r for r in results if r.ok]
            # verbose에서만 각 파일 OK 표시
            if self.verbose:
                for r in passed:
                    if r.file in skipped_set:
                        continue
                    rel = r.file.relative_to(self.project_root)
                    print(f"  OK    {rel}")
            # 실패는 항상 표시
            for r in failed:
                rel = r.file.relative_to(self.project_root)
                print(f"  FAIL  {rel}")
                for line in r.error.splitlines():
                    print(f"        {line}")
            if failed:
                save_cache(self.project_root, cache)
                self._ensure_gitignore()
                raise RuntimeError(
                    f"Syntax check failed: {len(failed)} of {len(results)} files"
                )
            newly_checked = len(passed) - len(skipped_files)
            # 요약: "Checked N, Skipped M"
            parts = []
            if newly_checked > 0:
                parts.append(f"Checked {newly_checked} file(s)")
            if skipped_files:
                parts.append(f"Skipped {len(skipped_files)} unchanged file(s)")
            if parts:
                print(", ".join(parts))

        # 캐시 저장
        save_cache(self.project_root, cache)

        # .gitignore 관리
        self._ensure_gitignore()

        # VSCode 설정 생성
        from stoke.ide.vscode import write_project_settings, make_python_settings

        if self.venv_exists():
            python_settings = make_python_settings(
                self.venv_python_exe(),
                self.project_root,
            )
            _, settings_changed = write_project_settings(self.project_root, python_settings)
            if settings_changed:
                print(f"IDE files updated: .vscode/settings.json")
        print(f"\nBuild complete: {self.target.name}")

    def run(self) -> int:
        """
        컴파일된 venv 파이썬으로 entry 파일 실행.
        반환: 종료 코드
        """
        if not self.target.entry:
            raise RuntimeError(
                f"Target '{self.target.name}' has no 'entry' field in stoke.toml.\n"
                f"  Add 'entry = \"src/main.py\"' under [targets.{self.target.name}]"
            )

        entry_path = self.project_root / self.target.entry
        if not entry_path.exists():
            raise RuntimeError(
                f"Entry file not found: {entry_path}\n"
                f"  Check the 'entry' field in stoke.toml"
            )

        if not self.venv_exists():
            raise RuntimeError(
                f"venv not found at {self.venv_dir}\n"
                f"  Run 'stoke build' first."
            )

        venv_python = self.venv_python_exe()
        print(f"Running: {entry_path}\n")
        try:
            result = subprocess.run(
                [str(venv_python), str(entry_path)],
                cwd=str(self.project_root),
            )
            return result.returncode
        except KeyboardInterrupt:
            return 130  # 130 = SIGINT (Ctrl+C 관행)

    def get_run_command(self) -> list[str]:
        """hot-reload용 실행 명령어."""
        if not self.target.entry:
            raise RuntimeError(
                f"Target '{self.target.name}' has no 'entry' field in stoke.toml.\n"
                f"  Add 'entry = \"src/main.py\"' under [targets.{self.target.name}]"
            )

        entry_path = self.project_root / self.target.entry
        if not entry_path.exists():
            raise RuntimeError(
                f"Entry file not found: {entry_path}\n"
                f"  Check the 'entry' field in stoke.toml"
            )

        if not self.venv_exists():
            raise RuntimeError(
                f"venv not found at {self.venv_dir}\n"
                f"  Run 'stoke build' first."
            )

        return [str(self.venv_python_exe()), str(entry_path)]