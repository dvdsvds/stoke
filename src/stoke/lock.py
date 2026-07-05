import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


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
class LockFile:
    python: PythonLock | None
    java: JavaLock | None
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

    if python_lock is None and java_lock is None:
        raise ValueError(
            f"Invalid lock file at {path}: missing [python] or [java] section"
        )

    meta = data.get("meta", {})

    return LockFile(
        python=python_lock,
        java=java_lock,
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

    content += "[packages]\n"
    if packages:
        for name in sorted(packages.keys()):
            content += f'{name} = "{packages[name]}"\n'

    content += f'''
[meta]
created_at = "{now}"
stoke_version = "0.3.0"
'''
    path.write_text(content, encoding="utf-8")
    return path


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