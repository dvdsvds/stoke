import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from stoke import __version__

@dataclass
class PythonLock:
    version: str
    executable: str


@dataclass
class JavaLock:
    version: str
    major_version: int
    java_home: str

@dataclass
class JavaDep:
    version: str
    sha1: str

@dataclass
class CLock:
    compiler: str      # "gcc"
    version: str       # "15.2.0"
    executable: str
    standard: str      # "c17"

@dataclass
class CppLock:
    compiler: str      # "g++"
    version: str       # "15.2.0"
    executable: str
    standard: str      # "c++17"


@dataclass
class CDep:
    version: str       # "10.2.1#1"
    triplet: str       # "x64-mingw-static"


@dataclass
class CppDep:
    version: str
    triplet: str

@dataclass
class LockFile:
    python: PythonLock | None
    java: JavaLock | None
    java_deps: dict[str, JavaDep]
    c: CLock | None
    cpp: CppLock | None
    c_deps: dict[str, CDep]
    cpp_deps: dict[str, CppDep]
    packages: dict[str, str]
    created_at: str
    stoke_version: str

def _lock_path(project_root: Path, lock_mode: str) -> Path:
    """lock_mode에 따라 lock 파일 경로 결정."""
    if lock_mode == "commit":
        return project_root / "stoke.lock"
    elif lock_mode == "local":
        return project_root / ".stoke" / "lock.toml"
    else:
        raise ValueError(f"Unknown lock_mode: {lock_mode}")


def load_lock(project_root: Path, lock_mode: str) -> LockFile | None:
    """lock 파일 읽기. 없으면 None."""
    path = _lock_path(project_root, lock_mode)
    if not path.exists():
        return None

    with open(path, "rb") as f:
        data = tomllib.load(f)

    # python 또는 java 중 하나는 있어야 함
    python_lock = None
    java_lock = None

    if "python" in data:
        python_data = data["python"]
        if "version" not in python_data:
            raise ValueError(f"Invalid lock file at {path}: missing python.version")
        python_lock = PythonLock(
            version=python_data["version"],
            executable=python_data.get("executable", ""),
        )

    if "java" in data:
        java_data = data["java"]
        if "version" not in java_data:
            raise ValueError(f"Invalid lock file at {path}: missing java.version")
        java_lock = JavaLock(
            version=java_data["version"],
            major_version=java_data.get("major_version", 0),
            java_home=java_data.get("java_home", ""),
        )

    # java_deps 파싱
    java_deps = {}
    if "java_deps" in data:
        for name, dep_data in data["java_deps"].items():
            if not isinstance(dep_data, dict):
                raise ValueError(
                    f"Invalid lock file at {path}: java_deps.{name} must be a table"
                )
            if "version" not in dep_data:
                raise ValueError(
                    f"Invalid lock file at {path}: missing java_deps.{name}.version"
                )
            java_deps[name] = JavaDep(
                version=dep_data["version"],
                sha1=dep_data.get("sha1", ""),
            )

    # c 파싱
    c_lock = None
    if "c" in data:
        c_data = data["c"]
        if "version" not in c_data:
            raise ValueError(f"Invalid lock file at {path}: missing c.version")
        c_lock = CLock(
            compiler=c_data.get("compiler", "gcc"),
            version=c_data["version"],
            executable=c_data.get("executable", ""),
            standard=c_data.get("standard", ""),
        )

    # cpp 파싱
    cpp_lock = None
    if "cpp" in data:
        cpp_data = data["cpp"]
        if "version" not in cpp_data:
            raise ValueError(f"Invalid lock file at {path}: missing cpp.version")
        cpp_lock = CppLock(
            compiler=cpp_data.get("compiler", "g++"),
            version=cpp_data["version"],
            executable=cpp_data.get("executable", ""),
            standard=cpp_data.get("standard", ""),
        )

    # c_deps 파싱
    c_deps = {}
    if "c_deps" in data:
        for name, dep_data in data["c_deps"].items():
            if not isinstance(dep_data, dict):
                raise ValueError(
                    f"Invalid lock file at {path}: c_deps.{name} must be a table"
                )
            if "version" not in dep_data:
                raise ValueError(
                    f"Invalid lock file at {path}: missing c_deps.{name}.version"
                )
            c_deps[name] = CDep(
                version=dep_data["version"],
                triplet=dep_data.get("triplet", ""),
            )

    # cpp_deps 파싱
    cpp_deps = {}
    if "cpp_deps" in data:
        for name, dep_data in data["cpp_deps"].items():
            if not isinstance(dep_data, dict):
                raise ValueError(
                    f"Invalid lock file at {path}: cpp_deps.{name} must be a table"
                )
            if "version" not in dep_data:
                raise ValueError(
                    f"Invalid lock file at {path}: missing cpp_deps.{name}.version"
                )
            cpp_deps[name] = CppDep(
                version=dep_data["version"],
                triplet=dep_data.get("triplet", ""),
            )

    meta = data.get("meta", {})

    return LockFile(
        python=python_lock,
        java=java_lock,
        java_deps=java_deps,
        c=c_lock,
        cpp=cpp_lock,
        c_deps=c_deps,
        cpp_deps=cpp_deps,
        packages=data.get("packages", {}),
        created_at=meta.get("created_at", ""),
        stoke_version=meta.get("stoke_version", ""),
    )

def save_lock(
    project_root: Path,
    lock_mode: str,
    python_version: str | None = None,
    python_executable: str | None = None,
    java_version: str | None = None,
    java_major_version: int | None = None,
    java_home: str | None = None,
    packages: dict[str, str] | None = None,
    java_deps: dict[str, "JavaDep"] | None = None,
    c_compiler: str | None = None,
    c_version: str | None = None,
    c_executable: str | None = None,
    c_standard: str | None = None,
    cpp_compiler: str | None = None,
    cpp_version: str | None = None,
    cpp_executable: str | None = None,
    cpp_standard: str | None = None,
    c_deps: dict[str, "CDep"] | None = None,
    cpp_deps: dict[str, "CppDep"] | None = None,
) -> Path:
    """
    lock 파일 쓰기. 저장된 경로 반환.
    python_* 또는 java_* 중 하나만 사용.
    """
    path = _lock_path(project_root, lock_mode)
    path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now().isoformat(timespec="seconds")

    content = ""

    if python_version is not None:
        escaped_exe = (python_executable or "").replace("\\", "\\\\")
        content += f'''[python]
version = "{python_version}"
executable = "{escaped_exe}"

'''

    if java_version is not None:
        escaped_home = (java_home or "").replace("\\", "\\\\")
        content += f'''[java]
version = "{java_version}"
major_version = {java_major_version or 0}
java_home = "{escaped_home}"

'''
    # java_deps 섹션
    if java_deps:
        content += "[java_deps]\n"
        for name in sorted(java_deps.keys()):
            dep = java_deps[name]
            content += f'"{name}" = {{ version = "{dep.version}", sha1 = "{dep.sha1}" }}\n'
        content += "\n"

    # c 섹션
    if c_version is not None:
        escaped_exe = (c_executable or "").replace("\\", "\\\\")
        content += f'''[c]
compiler = "{c_compiler or 'gcc'}"
version = "{c_version}"
executable = "{escaped_exe}"
standard = "{c_standard or ''}"

'''

    # cpp 섹션
    if cpp_version is not None:
        escaped_exe = (cpp_executable or "").replace("\\", "\\\\")
        content += f'''[cpp]
compiler = "{cpp_compiler or 'g++'}"
version = "{cpp_version}"
executable = "{escaped_exe}"
standard = "{cpp_standard or ''}"

'''

    # c_deps 섹션
    if c_deps:
        content += "[c_deps]\n"
        for name in sorted(c_deps.keys()):
            dep = c_deps[name]
            content += f'{name} = {{ version = "{dep.version}", triplet = "{dep.triplet}" }}\n'
        content += "\n"

    # cpp_deps 섹션
    if cpp_deps:
        content += "[cpp_deps]\n"
        for name in sorted(cpp_deps.keys()):
            dep = cpp_deps[name]
            content += f'{name} = {{ version = "{dep.version}", triplet = "{dep.triplet}" }}\n'
        content += "\n"

    content += "[packages]\n"

    if packages:
        for name in sorted(packages.keys()):
            content += f'{name} = "{packages[name]}"\n'

    content += f'''
[meta]
stoke_version = "{__version__}"
'''
    # 기존 내용이랑 같으면 write 스킵
    if path.exists():
        old_content = path.read_text(encoding="utf-8")
        if old_content == content:
            return path, False

    path.write_text(content, encoding="utf-8")
    return path, True


def is_compatible(lock_version: str, requested: str) -> bool:
    """
    lock에 저장된 버전이 stoke.toml의 요청 버전과 호환되는지 확인.
    예: lock='3.14.0', requested='3.14' -> True
    예: lock='3.14.0', requested='3.12' -> False
    """
    lock_parts = lock_version.split(".")
    req_parts = requested.split(".")

    # 요청한 부분 길이만큼만 비교 (앞부분만)
    for i in range(len(req_parts)):
        if i >= len(lock_parts):
            return False
        if lock_parts[i] != req_parts[i]:
            return False
    return True