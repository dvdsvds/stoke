import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompilerInstall:
    """C/C++ 컴파일러 정보."""
    kind: str          # "c" 또는 "cpp"
    version: str       # 예: "15.2.0"
    major_version: int # 예: 15
    executable: Path   # gcc 또는 g++ 경로
    is_default: bool = False


def _get_compiler_version(executable: str) -> str | None:
    """
    gcc --version 또는 g++ --version 실행해서 버전 문자열 추출.
    
    출력 예:
      gcc.exe (Rev8, Built by MSYS2 project) 15.2.0
      Copyright (C) 2025 Free Software Foundation, Inc.
    
    첫 줄에서 마지막 숫자.숫자.숫자 패턴 추출.
    """
    try:
        result = subprocess.run(
            [executable, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        first_line = result.stdout.splitlines()[0] if result.stdout else ""
        # 버전 패턴: X.Y.Z (숫자만)
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", first_line)
        if match:
            return match.group(0)
    except (subprocess.SubprocessError, FileNotFoundError, OSError, IndexError):
        pass
    return None


def _parse_major_version(version: str) -> int:
    """버전 문자열에서 메이저 버전 추출. '15.2.0' -> 15."""
    parts = version.split(".")
    if not parts:
        return 0
    try:
        return int(parts[0])
    except ValueError:
        return 0


def _detect_compiler(kind: str) -> CompilerInstall | None:
    """
    kind에 맞는 컴파일러 감지.
    kind: "c" -> gcc, "cpp" -> g++
    """
    if kind == "c":
        exe_name = "gcc"
    elif kind == "cpp":
        exe_name = "g++"
    else:
        raise ValueError(f"Unknown compiler kind: {kind}")

    exe_path = shutil.which(exe_name)
    if exe_path is None:
        return None

    version = _get_compiler_version(exe_path)
    if version is None:
        return None

    return CompilerInstall(
        kind=kind,
        version=version,
        major_version=_parse_major_version(version),
        executable=Path(exe_path),
        is_default=True,
    )


def detect_all() -> list[CompilerInstall]:
    """설치된 C/C++ 컴파일러 감지. C, C++ 각각."""
    installs = []
    for kind in ["c", "cpp"]:
        install = _detect_compiler(kind)
        if install is not None:
            installs.append(install)
    return installs


def find_compiler(kind: str, requested_version: str | None = None) -> CompilerInstall | None:
    """
    kind와 원하는 버전에 맞는 컴파일러 찾기.
    requested_version 없으면 시스템 default.
    """
    install = _detect_compiler(kind)
    if install is None:
        return None

    if requested_version is None:
        return install

    # 버전 매칭 (메이저 버전 또는 정확한 버전)
    try:
        target_major = int(requested_version)
        if install.major_version == target_major:
            return install
    except ValueError:
        if install.version == requested_version:
            return install
        if install.version.startswith(requested_version + "."):
            return install

    return None