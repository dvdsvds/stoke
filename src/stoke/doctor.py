"""stoke doctor -- 빠르고 읽기 전용인 환경 진단 (stoke build처럼 실제로 설치/컴파일하지 않음)."""
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from stoke.lock import load_lock
from stoke.tool_install import toolchain_env

@dataclass
class CheckResult:
    level: str  # "ok" | "warn" | "error"
    message: str

_LANGUAGE_EXE = {
    "go": ("go", "go.exe"),
    "rust": ("cargo", "cargo.exe"),
    "csharp": ("dotnet", "dotnet.exe"),
    "ruby": ("ruby", "ruby.exe"),
    "php": ("php", "php.exe"),
    "javascript": ("node", "node.exe"),
    "typescript": ("node", "node.exe"),
}

def _check_entry_and_sources(target, project_root: Path) -> list[CheckResult]:
    results = []
    if target.entry:
        entry_path = project_root / target.entry
        if not entry_path.exists():
            results.append(CheckResult("error", f"entry '{target.entry}' does not exist"))
    if target.sources:
        matched = any(list(project_root.glob(pattern)) for pattern in target.sources)
        if not matched:
            results.append(CheckResult("warn", f"sources {target.sources} match no files"))
    return results

_STOKE_LOCK_LANGUAGES = {"python", "java", "c", "cpp"}

# stoke.lock은 python/java/c/cpp만 관리함 -- 나머지 언어는 각자 생태계의 네이티브 lock 파일을 씀,
# stoke가 손대는 대상이 아님 (go.sum, Cargo.lock, package-lock.json 등).
_NATIVE_LOCK_FILE = {
    "go": "go.sum",
    "rust": "Cargo.lock",
    "javascript": "package-lock.json",
    "typescript": "package-lock.json",
    "ruby": "Gemfile.lock",
    "php": "composer.lock",
}

def _check_native_lock(target, project_root: Path) -> list[CheckResult]:
    lock_filename = _NATIVE_LOCK_FILE.get(target.language)
    if lock_filename is None:
        return []
    if (project_root / lock_filename).exists():
        return [CheckResult("ok", f"{lock_filename} found")]

    # go.sum은 의존성이 하나도 없으면 애초에 안 생김 -- go.mod에 require가 있을 때만 경고
    if target.language == "go":
        go_mod = project_root / "go.mod"
        if not go_mod.is_file() or "require" not in go_mod.read_text(encoding="utf-8", errors="replace"):
            return []

    return [CheckResult(
        "warn", f"no {lock_filename} found -- run 'stoke build' (or the language's own dependency command) once",
    )]

def _check_lock_file(config, target) -> list[CheckResult]:
    if target.language not in _STOKE_LOCK_LANGUAGES:
        return _check_native_lock(target, config.config_path.parent)

    lock = load_lock(config.config_path.parent, config.project.lock_mode)
    if lock is None:
        return [CheckResult("warn", "no lock file found -- run 'stoke build' once to create it")]

    results = [CheckResult("ok", "lock file found")]

    # python/java만 비교: stoke.toml의 버전 문자열이 lock의 실제 버전과 같은 형식(major[.minor])이라
    # 단순 prefix 비교가 성립함. c/cpp는 target.c_standard가 "c17" 같은 표준 플래그라 lock.c.version
    # (컴파일러 버전, 예: "15.2.0")과는 아예 다른 축이라 여기서 비교 대상이 아님.
    declared_version = {"python": target.python_version, "java": target.java_version}.get(target.language)
    locked = {"python": lock.python, "java": lock.java}.get(target.language)

    if declared_version and locked is not None and not locked.version.startswith(declared_version):
        results.append(CheckResult(
            "warn",
            f"stoke.toml wants {target.language} {declared_version} but lock has {locked.version} "
            f"-- 'stoke build' will reconcile this",
        ))

    if target.deps and target.language in ("python", "java"):
        locked_names = set(lock.packages) if target.language == "python" else set(lock.java_deps)
        missing = set(target.deps) - locked_names
        if missing:
            results.append(CheckResult(
                "warn", f"deps declared in stoke.toml but not in lock file yet: {', '.join(sorted(missing))} "
                f"-- 'stoke build' will install them",
            ))

    return results

def _check_python_env(config, target) -> list[CheckResult]:
    project_root = config.config_path.parent
    lang_dir = project_root / ".stoke" / "python" / target.name
    venv_dir = lang_dir / ("conda_env" if target.env_type == "conda" else "venv")

    if not venv_dir.is_dir():
        return [CheckResult("warn", f"no {target.env_type} found at {venv_dir} -- run 'stoke build' to create it")]

    exe_name = "python.exe" if sys.platform == "win32" else "python"
    python_exe = venv_dir / ("Scripts" if sys.platform == "win32" and target.env_type != "conda" else "") / exe_name
    if not python_exe.is_file():
        python_exe = venv_dir / "bin" / exe_name if sys.platform != "win32" else venv_dir / exe_name
    if not python_exe.is_file():
        return [CheckResult("error", f"{venv_dir} exists but has no runnable python executable")]

    results = [CheckResult("ok", f"venv python: {python_exe}")]

    lock = load_lock(project_root, config.project.lock_mode)
    if lock is not None and lock.packages:
        pip_exe = python_exe.parent / ("pip.exe" if sys.platform == "win32" else "pip")
        if pip_exe.is_file():
            result = subprocess.run(
                [str(pip_exe), "freeze", "--disable-pip-version-check"],
                capture_output=True, text=True, errors="replace", timeout=15,
            )
            if result.returncode == 0:
                installed = {}
                for line in result.stdout.splitlines():
                    if "==" in line and not line.startswith("#"):
                        name, _, version = line.strip().partition("==")
                        installed[name] = version
                if installed != lock.packages:
                    results.append(CheckResult(
                        "warn", "installed packages differ from lock file -- run 'stoke build' to reconcile",
                    ))
    return results

def _check_toolchain(config, target) -> list[CheckResult]:
    project_root = config.config_path.parent
    language = target.language

    if language == "python":
        return _check_python_env(config, target)

    if language == "java" or language == "kotlin":
        lock = load_lock(project_root, config.project.lock_mode)
        if lock is None or lock.java is None:
            return [CheckResult("warn", "no locked JDK found -- run 'stoke build' once")]
        if not Path(lock.java.java_home).is_dir():
            return [CheckResult("error", f"locked JAVA_HOME does not exist: {lock.java.java_home}")]
        return [CheckResult("ok", f"JDK: {lock.java.java_home}")]

    if language in ("c", "cpp"):
        lock = load_lock(project_root, config.project.lock_mode)
        locked = getattr(lock, language, None) if lock else None
        if locked is None:
            return [CheckResult("warn", "no locked compiler found -- run 'stoke build' once")]
        if locked.executable and not Path(locked.executable).exists() and shutil.which(locked.executable) is None:
            return [CheckResult("error", f"locked compiler not found: {locked.executable}")]
        return [CheckResult("ok", f"compiler: {locked.compiler} {locked.version}")]

    if language in ("javascript", "typescript"):
        from stoke.languages._node_tools import find_node
        try:
            node_exe = find_node(project_root)
        except RuntimeError as e:
            return [CheckResult("error", str(e))]
        return [CheckResult("ok", f"node: {node_exe}")]

    exe_names = _LANGUAGE_EXE.get(language)
    if exe_names is None:
        return [CheckResult("warn", f"no toolchain check implemented for '{language}' yet")]

    env = toolchain_env(language, project_root)
    exe_name = exe_names[1] if sys.platform == "win32" else exe_names[0]
    found = shutil.which(exe_name, path=env.get("PATH"))
    if found is None:
        return [CheckResult("error", f"'{exe_name}' not found in PATH or project-local toolchain")]
    return [CheckResult("ok", f"{exe_name}: {found}")]

def _check_gitignore(config) -> list[CheckResult]:
    if config.project.lock_mode != "commit":
        return []
    project_root = config.config_path.parent
    gitignore = project_root / ".gitignore"
    if not gitignore.is_file():
        return []
    try:
        lines = [l.strip() for l in gitignore.read_text(encoding="utf-8").splitlines()]
    except OSError:
        return []
    if any(l in ("stoke.lock", "*.lock") for l in lines if l and not l.startswith("#")):
        return [CheckResult(
            "warn",
            "lock_mode is 'commit' but .gitignore appears to ignore stoke.lock -- "
            "teammates/CI won't get the same reproducible build",
        )]
    return []

def run_checks(config, target) -> list[CheckResult]:
    project_root = config.config_path.parent
    results = []
    results.extend(_check_entry_and_sources(target, project_root))
    results.extend(_check_lock_file(config, target))
    results.extend(_check_toolchain(config, target))
    results.extend(_check_gitignore(config))
    return results
