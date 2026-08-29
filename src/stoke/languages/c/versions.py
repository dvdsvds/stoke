import locale
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CompilerInstall:
    """C/C++ 컴파일러 정보."""
    kind: str          # "c" 또는 "cpp"
    version: str       # 예: "15.2.0"
    major_version: int # 예: 15
    executable: Path   # gcc/g++/cl 경로
    is_default: bool = False
    family: str = "gcc"          # "gcc" / "clang" / "msvc"
    vcvars_bat: Path | None = None  # msvc만 사용 (INCLUDE/LIB 환경변수 설정용)

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
            errors="replace",
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

def _find_vswhere() -> Path | None:
    """Visual Studio 설치 검색 도구 vswhere.exe 위치 (VS 인스톨러가 항상 같이 깔아둠)."""
    default = (
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    )
    if default.is_file():
        return default
    found = shutil.which("vswhere")
    return Path(found) if found else None

def _find_msvc_install() -> tuple[Path, Path] | None:
    """
    설치된 Visual Studio에서 cl.exe와 vcvars64.bat 경로를 찾음.
    반환: (cl.exe 경로, vcvars64.bat 경로) 또는 못 찾으면 None.
    """
    vswhere = _find_vswhere()
    if vswhere is None:
        return None
    try:
        result = subprocess.run(
            [str(vswhere), "-latest", "-products", "*",
             "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
             "-property", "installationPath"],
            capture_output=True, text=True, errors="replace", timeout=10,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    install_path = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    if not install_path:
        return None

    vs_root = Path(install_path)
    vcvars64 = vs_root / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
    tools_root = vs_root / "VC" / "Tools" / "MSVC"
    if not vcvars64.is_file() or not tools_root.is_dir():
        return None

    def _version_key(d: Path) -> tuple:
        return tuple(int(p) if p.isdigit() else 0 for p in d.name.split("."))

    version_dirs = sorted((d for d in tools_root.iterdir() if d.is_dir()), key=_version_key, reverse=True)
    for version_dir in version_dirs:
        for host_arch in ("Hostx64/x64", "Hostx86/x86"):
            cl_path = version_dir / "bin" / Path(host_arch)
            cl_path = cl_path / "cl.exe"
            if cl_path.is_file():
                return cl_path, vcvars64
    return None

def _get_msvc_version(cl_path: Path) -> str | None:
    """cl.exe를 인자 없이 실행하면 stderr에 버전 배너가 나옴 (로케일 무관하게 숫자 패턴만 추출)."""
    try:
        # cl.exe 배너는 OS 콘솔 코드페이지로 나옴 (UTF-8 아님) -- base.py의
        # _output_encoding()과 같은 이유.
        result = subprocess.run(
            [str(cl_path)], capture_output=True, text=True,
            encoding=locale.getpreferredencoding(False), errors="replace", timeout=5,
        )
        first_line = result.stderr.splitlines()[0] if result.stderr else ""
        match = re.search(r"(\d+)\.(\d+)\.(\d+)", first_line)
        if match:
            return match.group(0)
    except (subprocess.SubprocessError, OSError, IndexError):
        pass
    return None

_msvc_install_cache: dict = {}

def _detect_msvc(kind: str) -> CompilerInstall | None:
    """cl.exe 감지. C/C++ 공용 (같은 실행 파일, 표준 플래그만 다름)."""
    if "value" not in _msvc_install_cache:
        _msvc_install_cache["value"] = _find_msvc_install()
    found = _msvc_install_cache["value"]
    if found is None:
        return None
    cl_path, vcvars64 = found
    version = _get_msvc_version(cl_path)
    if version is None:
        return None
    return CompilerInstall(
        kind=kind,
        version=version,
        major_version=_parse_major_version(version),
        executable=cl_path,
        is_default=True,
        family="msvc",
        vcvars_bat=vcvars64,
    )

def _detect_compiler(kind: str, compiler_family: str = "gcc") -> CompilerInstall | None:
    """
    kind에 맞는 컴파일러 감지.
    kind: "c" -> gcc/clang/cl, "cpp" -> g++/clang++/cl
    compiler_family: "gcc", "clang", 또는 "msvc"
    """
    if compiler_family == "msvc":
        return _detect_msvc(kind)

    if compiler_family == "gcc":
        if kind == "c":
            exe_name = "gcc"
        elif kind == "cpp":
            exe_name = "g++"
        else:
            raise ValueError(f"Unknown compiler kind: {kind}")
    elif compiler_family == "clang":
        if kind == "c":
            exe_name = "clang"
        elif kind == "cpp":
            exe_name = "clang++"
        else:
            raise ValueError(f"Unknown compiler kind: {kind}")
    else:
        raise ValueError(f"Unknown compiler family: {compiler_family}")

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
        family=compiler_family,
    )

def _detect_local(kind: str, project_root: Path) -> CompilerInstall | None:
    """프로젝트의 .stoke/toolchains/gcc-*/ 에서 stoke install로 받은 gcc/g++ 감지.
    mingw-builds 7z는 안에 mingw64/ 폴더가 한 겹 더 있음."""
    toolchains = project_root / ".stoke" / "toolchains"
    if not toolchains.is_dir():
        return None

    if sys.platform == "win32":
        exe_name = "gcc.exe" if kind == "c" else "g++.exe"
    else:
        exe_name = "gcc" if kind == "c" else "g++"

    for d in sorted(toolchains.iterdir()):
        if not d.is_dir() or not d.name.startswith("gcc-"):
            continue
        candidates = [d / "bin" / exe_name] + list(d.glob(f"*/bin/{exe_name}"))
        for exe in candidates:
            if exe.is_file():
                version = _get_compiler_version(str(exe))
                if version is None:
                    continue
                return CompilerInstall(
                    kind=kind,
                    version=version,
                    major_version=_parse_major_version(version),
                    executable=exe,
                    is_default=False,
                    family="gcc",
                )
    return None

def detect_all() -> list[CompilerInstall]:
    """설치된 C/C++ 컴파일러 감지. C, C++ 각각 (gcc/clang) + MSVC."""
    installs = []
    for kind in ["c", "cpp"]:
        install = _detect_compiler(kind)
        if install is not None:
            installs.append(install)
    for kind in ["c", "cpp"]:
        install = _detect_msvc(kind)
        if install is not None:
            installs.append(install)
    return installs

def _version_matches(install: CompilerInstall, requested_version: str) -> bool:
    try:
        target_major = int(requested_version)
        return install.major_version == target_major
    except ValueError:
        return install.version == requested_version or install.version.startswith(requested_version + ".")

def find_compiler(
    kind: str,
    requested_version: str | None = None,
    compiler_family: str = "gcc",
    project_root: Path | None = None,
) -> CompilerInstall | None:
    """
    kind와 원하는 버전에 맞는 컴파일러 찾기.
    requested_version 없으면 시스템 default.
    compiler_family: "gcc" 또는 "clang"
    project_root가 주어지면 프로젝트 로컬 설치(.stoke/toolchains)를 시스템보다 우선 확인.
    """
    if project_root is not None and compiler_family == "gcc":
        local = _detect_local(kind, project_root)
        if local is not None and (requested_version is None or _version_matches(local, requested_version)):
            return local

    install = _detect_compiler(kind, compiler_family=compiler_family)
    if install is None:
        return None

    if requested_version is None:
        return install

    if _version_matches(install, requested_version):
        return install

    return None