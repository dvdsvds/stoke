import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class PythonLock:
    version: str
    executable: str


@dataclass
class LockFile:
    python: PythonLock
    packages: dict[str, str]  # {패키지명: 버전} 예: {"requests": "2.31.0"}
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

    if "python" not in data:
        raise ValueError(f"Invalid lock file at {path}: missing [python] section")

    python_data = data["python"]
    if "version" not in python_data:
        raise ValueError(f"Invalid lock file at {path}: missing python.version")

    meta = data.get("meta", {})

    return LockFile(
        python=PythonLock(
            version=python_data["version"],
            executable=python_data.get("executable", ""),
        ),
        packages=data.get("packages", {}),
        created_at=meta.get("created_at", ""),
        stoke_version=meta.get("stoke_version", ""),
    )


def save_lock(
    project_root: Path,
    lock_mode: str,
    python_version: str,
    python_executable: str,
    packages: dict[str, str] | None = None,
) -> Path:
    """lock 파일 쓰기. 저장된 경로 반환."""
    path = _lock_path(project_root, lock_mode)
    path.parent.mkdir(parents=True, exist_ok=True)

    escaped_exe = python_executable.replace("\\", "\\\\")
    now = datetime.now().isoformat(timespec="seconds")

    content = f'''[python]
version = "{python_version}"
executable = "{escaped_exe}"

[packages]
'''
    if packages:
        # 알파벳순으로 저장 (diff 안정성)
        for name in sorted(packages.keys()):
            content += f'{name} = "{packages[name]}"\n'

    content += f'''
[meta]
created_at = "{now}"
stoke_version = "0.1.0"
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