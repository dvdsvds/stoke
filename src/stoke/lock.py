import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from stoke import __version__

@dataclass
class PythonLock:
    version: str
    executable: str
    def to_toml_section(self) -> str:
        escaped = self.executable.replace("\\", "\\\\")
        return f'[python]\nversion = "{self.version}"\nexecutable = "{escaped}"\n\n'
    @classmethod
    def from_dict(cls, d: dict) -> "PythonLock":
        if "version" not in d:
            raise KeyError("version")
        return cls(version=d["version"], executable=d.get("executable", ""))

@dataclass
class JavaLock:
    version: str
    major_version: int
    java_home: str
    def to_toml_section(self) -> str:
        escaped = self.java_home.replace("\\", "\\\\")
        return f'[java]\nversion = "{self.version}"\nmajor_version = {self.major_version}\njava_home = "{escaped}"\n\n'
    @classmethod
    def from_dict(cls, d: dict) -> "JavaLock":
        if "version" not in d:
            raise KeyError("version")
        return cls(version=d["version"], major_version=d.get("major_version", 0), java_home=d.get("java_home", ""))

@dataclass
class JavaDep:
    version: str
    sha1: str
    def to_toml_line(self, name: str) -> str:
        return f'"{name}" = {{ version = "{self.version}", sha1 = "{self.sha1}" }}\n'
    @classmethod
    def from_dict(cls, d: dict) -> "JavaDep":
        if "version" not in d:
            raise KeyError("version")
        return cls(version=d["version"], sha1=d.get("sha1", ""))

@dataclass
class CLock:
    compiler: str      # "gcc"
    version: str       # "15.2.0"
    executable: str
    standard: str      # "c17"
    def to_toml_section(self) -> str:
        escaped = self.executable.replace("\\", "\\\\")
        return f'[c]\ncompiler = "{self.compiler}"\nversion = "{self.version}"\nexecutable = "{escaped}"\nstandard = "{self.standard}"\n\n'
    @classmethod
    def from_dict(cls, d: dict) -> "CLock":
        if "version" not in d:
            raise KeyError("version")
        return cls(compiler=d.get("compiler", "gcc"), version=d["version"], executable=d.get("executable", ""), standard=d.get("standard", ""))

@dataclass
class CppLock:
    compiler: str      # "g++"
    version: str       # "15.2.0"
    executable: str
    standard: str      # "c++17"
    def to_toml_section(self) -> str:
        escaped = self.executable.replace("\\", "\\\\")
        return f'[cpp]\ncompiler = "{self.compiler}"\nversion = "{self.version}"\nexecutable = "{escaped}"\nstandard = "{self.standard}"\n\n'
    @classmethod
    def from_dict(cls, d: dict) -> "CppLock":
        if "version" not in d:
            raise KeyError("version")
        return cls(compiler=d.get("compiler", "g++"), version=d["version"], executable=d.get("executable", ""), standard=d.get("standard", ""))

@dataclass
class CDep:
    version: str       # "10.2.1#1"
    triplet: str       # "x64-mingw-static"
    def to_toml_line(self, name: str) -> str:
        return f'{name} = {{ version = "{self.version}", triplet = "{self.triplet}" }}\n'
    @classmethod
    def from_dict(cls, d: dict) -> "CDep":
        if "version" not in d:
            raise KeyError("version")
        return cls(version=d["version"], triplet=d.get("triplet", ""))

@dataclass
class CppDep:
    version: str
    triplet: str
    def to_toml_line(self, name: str) -> str:
        return f'{name} = {{ version = "{self.version}", triplet = "{self.triplet}" }}\n'
    @classmethod
    def from_dict(cls, d: dict) -> "CppDep":
        if "version" not in d:
            raise KeyError("version")
        return cls(version=d["version"], triplet=d.get("triplet", ""))

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

def _parse_section(data: dict, key: str, cls, path: Path):
    if key not in data:
        return None
    try:
        return cls.from_dict(data[key])
    except KeyError as e:
        raise ValueError(f"Invalid lock file at {path}: missing {key}.{e.args[0]}")

def _parse_deps_section(data: dict, key: str, cls, path: Path) -> dict:
    result = {}
    if key in data:
        for name, dep_data in data[key].items():
            if not isinstance(dep_data, dict):
                raise ValueError(f"Invalid lock file at {path}: {key}.{name} must be a table")
            try:
                result[name] = cls.from_dict(dep_data)
            except KeyError as e:
                raise ValueError(f"Invalid lock file at {path}: missing {key}.{name}.{e.args[0]}")
    return result

def load_lock(project_root: Path, lock_mode: str) -> LockFile | None:
    """lock 파일 읽기. 없으면 None."""
    path = _lock_path(project_root, lock_mode)
    if not path.exists():
        return None

    with open(path, "rb") as f:
        data = tomllib.load(f)

    python_lock = _parse_section(data, "python", PythonLock, path)
    java_lock = _parse_section(data, "java", JavaLock, path)
    java_deps = _parse_deps_section(data, "java_deps", JavaDep, path)
    c_lock = _parse_section(data, "c", CLock, path)
    cpp_lock = _parse_section(data, "cpp", CppLock, path)
    c_deps = _parse_deps_section(data, "c_deps", CDep, path)
    cpp_deps = _parse_deps_section(data, "cpp_deps", CppDep, path)

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

def _render_deps_section(header: str, deps: dict) -> str:
    if not deps:
        return ""
    lines = [f"[{header}]"] + [deps[name].to_toml_line(name).rstrip("\n") for name in sorted(deps)]
    return "\n".join(lines) + "\n\n"

def save_lock(
    project_root: Path,
    lock_mode: str,
    python: PythonLock | None = None,
    java: JavaLock | None = None,
    c: CLock | None = None,
    cpp: CppLock | None = None,
    java_deps: dict[str, JavaDep] | None = None,
    c_deps: dict[str, CDep] | None = None,
    cpp_deps: dict[str, CppDep] | None = None,
    packages: dict[str, str] | None = None,
) -> Path:
    """
    lock 파일 쓰기. 저장된 경로 반환.
    python_* 또는 java_* 중 하나만 사용.
    """
    path = _lock_path(project_root, lock_mode)
    path.parent.mkdir(parents=True, exist_ok=True)

    # 다중 언어 타켓이 lock 파일 하나를 공유하므로, 호출자가 안 준 섹션은
    # 기존 lock 파일 값으로 채워서 다른 언어/타겟 정보를 덮어쓰지 않게 함
    existing = load_lock(project_root, lock_mode)
    if existing is not None:
        if python is None:
            python = existing.python
        if java is None:
            java = existing.java
        if c is None:
            c = existing.c
        if cpp is None:
            cpp = existing.cpp
        if java_deps is None:
            java_deps = existing.java_deps
        if c_deps is None:
            c_deps = existing.c_deps
        if cpp_deps is None:
            cpp_deps = existing.cpp_deps
        if packages is None:
            packages = existing.packages

    content = ""

    if python is not None:
        content += python.to_toml_section()
    if java is not None:
        content += java.to_toml_section()
    content += _render_deps_section("java_deps", java_deps or {})
    if c is not None:
        content += c.to_toml_section()
    if cpp is not None:
        content += cpp.to_toml_section()
    content += _render_deps_section("c_deps", c_deps or {})
    content += _render_deps_section("cpp_deps", cpp_deps or {})
    content += "[packages]\n"
    for name in sorted((packages or {}).keys()):
        content += f'{name} = "{packages[name]}"\n'
    content += f'\n[meta]\nstoke_version = "{__version__}"\n'

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