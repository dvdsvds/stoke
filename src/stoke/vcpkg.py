"""
vcpkg 관리 모듈.
stoke가 vcpkg를 다운로드/설치/관리해요.
저장 위치: ~/.stoke/tools/vcpkg/
"""

import platform
import shutil
import subprocess
from pathlib import Path


def check_git_installed() -> bool:
    """git이 시스템에 설치돼있는지 확인."""
    return shutil.which("git") is not None


def get_vcpkg_root() -> Path:
    """stoke가 관리하는 vcpkg 저장 위치."""
    return Path.home() / ".stoke" / "tools" / "vcpkg"


def get_vcpkg_executable() -> Path:
    """vcpkg 실행 파일 경로. Windows는 .exe, 다른 곳은 확장자 없음."""
    root = get_vcpkg_root()
    if platform.system() == "Windows":
        return root / "vcpkg.exe"
    return root / "vcpkg"


def is_vcpkg_installed() -> bool:
    """vcpkg가 설치됐는지 확인. 실행 파일 존재로 판단."""
    return get_vcpkg_executable().is_file()


def get_vcpkg_version() -> str | None:
    """
    설치된 vcpkg 버전 반환.
    미설치 또는 실행 실패 시 None.
    """
    if not is_vcpkg_installed():
        return None

    try:
        result = subprocess.run(
            [str(get_vcpkg_executable()), "version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        # 출력 예: "vcpkg package management program version 2024-01-01"
        first_line = result.stdout.splitlines()[0] if result.stdout else ""
        # "version" 뒤 부분 추출
        if "version" in first_line:
            parts = first_line.split("version")
            if len(parts) >= 2:
                return parts[-1].strip()
        return first_line
    except (subprocess.SubprocessError, OSError, IndexError):
        return None

def install_vcpkg() -> None:
    """
    vcpkg 다운로드 + bootstrap 실행.
    실패 시 RuntimeError.
    """
    # git 확인
    if not check_git_installed():
        raise RuntimeError(
            "git is required to install vcpkg.\n"
            "  Install git from https://git-scm.com"
        )

    root = get_vcpkg_root()
    root.parent.mkdir(parents=True, exist_ok=True)

    # 이미 있으면 에러
    if root.exists():
        raise RuntimeError(
            f"vcpkg already exists at {root}\n"
            f"  Use 'stoke uninstall vcpkg' first to remove it"
        )

    # git clone
    print(f"Cloning vcpkg to {root}...")
    result = subprocess.run(
        [
            "git", "clone",
            "--depth", "1",
            "https://github.com/microsoft/vcpkg.git",
            str(root),
        ],
    )
    if result.returncode != 0:
        raise RuntimeError(f"git clone failed (exit code {result.returncode})")

    # bootstrap 스크립트 실행
    if platform.system() == "Windows":
        bootstrap_script = root / "bootstrap-vcpkg.bat"
    else:
        bootstrap_script = root / "bootstrap-vcpkg.sh"

    if not bootstrap_script.is_file():
        raise RuntimeError(
            f"bootstrap script not found: {bootstrap_script}\n"
            f"  vcpkg clone may be incomplete"
        )

    print(f"\nRunning bootstrap script...")
    result = subprocess.run(
        [str(bootstrap_script), "-disableMetrics"],
        cwd=str(root),
        shell=(platform.system() == "Windows"),
    )
    if result.returncode != 0:
        raise RuntimeError(f"bootstrap failed (exit code {result.returncode})")

    # 실행 파일 확인
    if not is_vcpkg_installed():
        raise RuntimeError(
            f"vcpkg installation completed but executable not found at {get_vcpkg_executable()}"
        )

    print(f"\nvcpkg installed successfully at {root}")


def uninstall_vcpkg() -> None:
    """vcpkg 삭제."""
    root = get_vcpkg_root()

    if not root.exists():
        raise RuntimeError(f"vcpkg is not installed at {root}")

    print(f"Removing vcpkg at {root}...")

    # Windows에서 읽기 전용 파일 처리
    def onerror(func, path, exc_info):
        import os
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(str(root), onexc=onerror)

    print("vcpkg removed successfully")

def install_library(name: str, version: str | None = None, triplet: str | None = None) -> None:
    """
    vcpkg로 라이브러리 설치.
    name: 라이브러리 이름 (예: "fmt")
    version: 특정 버전 (없으면 최신)
    triplet: vcpkg triplet (없으면 자동 감지, gcc 기준)
    실패 시 RuntimeError.
    """
    if not is_vcpkg_installed():
        raise RuntimeError(
            "vcpkg is not installed.\n"
            "  Run 'stoke install vcpkg' first"
        )

    if triplet is None:
        triplet = get_triplet()

    # vcpkg 명령어 조합
    exe = get_vcpkg_executable()
    # triplet 지정: "name:triplet"
    package_spec = f"{name}:{triplet}"

    if version is None:
        cmd = [str(exe), "install", package_spec]
    else:
        cmd = [str(exe), "install", package_spec, f"--version={version}"]

    print(f"Installing {name} ({triplet})" + (f" version {version}" if version else " (latest)") + "...")
    result = subprocess.run(cmd, cwd=str(get_vcpkg_root()))
    if result.returncode != 0:
        raise RuntimeError(
            f"vcpkg install failed for {name}"
            + (f" version {version}" if version else "")
            + f" (exit code {result.returncode})"
        )
    print(f"\n{name} installed successfully")

def remove_library(name: str, triplet: str | None = None) -> None:
    """
    vcpkg로 라이브러리 제거.
    triplet: vcpkg triplet (없으면 자동 감지, gcc 기준)
    실패 시 RuntimeError.
    """
    if not is_vcpkg_installed():
        raise RuntimeError(
            "vcpkg is not installed.\n"
            "  Run 'stoke install vcpkg' first"
        )

    if triplet is None:
        triplet = get_triplet()

    exe = get_vcpkg_executable()
    package_spec = f"{name}:{triplet}"
    cmd = [str(exe), "remove", package_spec]

    print(f"Removing {name} ({triplet})...")
    result = subprocess.run(cmd, cwd=str(get_vcpkg_root()))
    if result.returncode != 0:
        raise RuntimeError(
            f"vcpkg remove failed for {name} (exit code {result.returncode})"
        )
    print(f"\n{name} removed successfully")

def list_installed_libraries() -> list[str]:
    """
    vcpkg에 설치된 라이브러리 목록 반환.
    반환: 라이브러리 이름 리스트.
    """
    if not is_vcpkg_installed():
        return []

    exe = get_vcpkg_executable()
    try:
        result = subprocess.run(
            [str(exe), "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []

        # 출력 형식 예:
        # fmt:x64-windows                             10.2.1#1  ...
        # spdlog:x64-windows                          1.14.0    ...
        libraries = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("The"):
                continue
            # 첫 컬럼에서 ":" 앞부분 추출
            first_col = line.split()[0] if line.split() else ""
            if ":" in first_col:
                lib_name = first_col.split(":")[0]
                if lib_name and lib_name not in libraries:
                    libraries.append(lib_name)

        return libraries
    except (subprocess.SubprocessError, OSError):
        return []

def get_triplet(compiler_kind: str = "gcc") -> str:
    """
    플랫폼 + 컴파일러 종류에 따라 vcpkg triplet 결정.

    compiler_kind:
      "gcc" / "g++" / "clang": mingw 계열 → x64-mingw-static
      "msvc" / "cl": MSVC → x64-windows

    사용자가 다른 triplet 원하면 나중에 stoke.toml에서 명시 가능.
    """
    import platform

    system = platform.system()
    machine = platform.machine().lower()

    # Windows의 경우 컴파일러 종류에 따라 다름
    if system == "Windows":
        # MSVC는 x64-windows
        if compiler_kind in ("msvc", "cl"):
            if "arm" in machine or "aarch64" in machine:
                return "arm64-windows"
            elif "64" in machine:
                return "x64-windows"
            else:
                return "x86-windows"
        # gcc/g++/clang (mingw)은 x64-mingw-static
        else:
            if "arm" in machine or "aarch64" in machine:
                return "arm64-mingw-static"
            else:
                return "x64-mingw-static"
    elif system == "Linux":
        if "aarch64" in machine or "arm64" in machine:
            return "arm64-linux"
        else:
            return "x64-linux"
    elif system == "Darwin":  # macOS
        if "arm" in machine or "aarch64" in machine:
            return "arm64-osx"
        else:
            return "x64-osx"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

def get_installed_dir(triplet: str | None = None) -> Path:
    """
    vcpkg의 라이브러리 설치 위치.
    triplet 없으면 자동 감지.
    """
    if triplet is None:
        triplet = get_triplet()
    return get_vcpkg_root() / "installed" / triplet


def get_include_dir(triplet: str | None = None) -> Path:
    """vcpkg의 헤더 경로."""
    return get_installed_dir(triplet) / "include"


def get_lib_dir(triplet: str | None = None) -> Path:
    """vcpkg의 라이브러리 경로."""
    return get_installed_dir(triplet) / "lib"


def is_library_installed(name: str, triplet: str | None = None) -> bool:
    """
    특정 라이브러리가 이미 설치돼있는지 확인.
    """
    if not is_vcpkg_installed():
        return False

    # installed/vcpkg/info 폴더에 파일 있으면 설치됨
    if triplet is None:
        triplet = get_triplet()

    info_dir = get_vcpkg_root() / "installed" / "vcpkg" / "info"
    if not info_dir.is_dir():
        return False

    # 파일명 예: fmt_10.2.1_x64-windows.list
    for f in info_dir.glob(f"{name}_*_{triplet}.list"):
        return True

    return False

def get_installed_library_version(name: str, triplet: str | None = None) -> str | None:
    """
    vcpkg에 설치된 라이브러리의 실제 버전 반환.
    installed/vcpkg/info/<name>_<version>_<triplet>.list 파일명에서 추출.
    미설치 시 None.
    """
    if not is_vcpkg_installed():
        return None

    if triplet is None:
        triplet = get_triplet()

    info_dir = get_vcpkg_root() / "installed" / "vcpkg" / "info"
    if not info_dir.is_dir():
        return None

    # 파일명 형식: name_version_triplet.list
    # 예: fmt_10.2.1_x64-mingw-static.list
    for f in info_dir.glob(f"{name}_*_{triplet}.list"):
        stem = f.stem  # 확장자 제거
        # name_ 제거
        rest = stem[len(name) + 1:]
        # _triplet 제거
        version = rest[:-(len(triplet) + 1)]
        return version

    return None