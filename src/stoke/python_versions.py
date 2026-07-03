import subprocess
import sys
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PythonInstall:
    version: str          # 예: "3.12.12"
    executable: Path      # 실행파일 절대 경로
    is_default: bool = False


def _get_version(exe: str) -> str | None:
    """실행파일에 --version 물어봐서 버전 문자열 얻기"""
    try:
        result = subprocess.run(
            [exe, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # 출력 예: "Python 3.12.12"
        output = (result.stdout or result.stderr).strip()
        if output.startswith("Python "):
            return output[len("Python "):].strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    return None


def _detect_via_py_launcher() -> list[PythonInstall]:
    """윈도우 py launcher(`py -0p`)로 감지"""
    installs = []
    try:
        result = subprocess.run(
            ["py", "-0p"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return []

    # 출력 예:
    #  -V:3.14 *        C:\Users\...\Python314\python.exe
    #  -V:3.12          C:\...\python.exe
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line.startswith("-V:"):
            continue

        # "-V:3.14"에서 버전 뽑기
        first_space = line.find(" ")
        if first_space == -1:
            continue
        short_ver = line[3:first_space]  # "-V:" 제거
        rest = line[first_space:].strip()

        # 기본 파이썬은 앞에 "*"
        # is_default = rest.startswith("*")
        if rest.startswith("*"):
            rest = rest[1:].strip()
        is_default = False

        exe_path = Path(rest)
        if not exe_path.exists():
            continue

        # 정확한 버전 얻기
        full_ver = _get_version(str(exe_path)) or short_ver

        installs.append(PythonInstall(
            version=full_ver,
            executable=exe_path.resolve(),
            is_default=is_default,
        ))

    return installs


def _detect_via_path_scan() -> list[PythonInstall]:
    """PATH에서 python, python3, python3.x 찾기 (크로스 플랫폼)"""
    candidates = ["python", "python3"]
    # 3.8 ~ 3.14 명시 검색
    for minor in range(8, 15):
        candidates.append(f"python3.{minor}")

    seen_paths = set()
    installs = []

    for name in candidates:
        exe = shutil.which(name)
        if not exe:
            continue

        # 절대 경로로 정규화 (같은 실행파일 중복 방지)
        real_path = Path(exe).resolve()
        if real_path in seen_paths:
            continue
        seen_paths.add(real_path)

        version = _get_version(exe)
        if version is None:
            continue

        installs.append(PythonInstall(
            version=version,
            executable=real_path,
            is_default=False,
        ))

    return installs


def detect_all() -> list[PythonInstall]:
    """설치된 모든 파이썬 감지 (윈도우면 py launcher 우선)"""
    raw_installs = []

    # 1. 윈도우: py launcher 시도
    if sys.platform == "win32":
        raw_installs.extend(_detect_via_py_launcher())

    # 2. PATH 스캔
    raw_installs.extend(_detect_via_path_scan())

    # 3. 중복 제거: (버전, 파일 크기) 기준
    #    윈도우 심볼릭/하드링크는 resolve()로 감지 안 되는 경우가 있어서
    #    파일 크기까지 봐서 판별
    seen = set()
    installs = []
    for install in raw_installs:
        try:
            size = install.executable.stat().st_size
        except OSError:
            continue

        key = (install.version, size)
        if key in seen:
            continue
        seen.add(key)
        installs.append(install)

    # 4. 진짜 default 결정: 터미널에서 'python' 쳤을 때 실행되는 것
    default_exe = shutil.which("python")
    if default_exe:
        try:
            default_size = Path(default_exe).stat().st_size
            default_ver = _get_version(default_exe)
            for install in installs:
                try:
                    ins_size = install.executable.stat().st_size
                except OSError:
                    continue
                if ins_size == default_size and install.version == default_ver:
                    install.is_default = True
                    break
        except OSError:
            pass

    # 5. 버전 내림차순 정렬
    installs.sort(key=lambda x: _version_tuple(x.version), reverse=True)

    return installs


def _version_tuple(v: str) -> tuple:
    """버전 문자열을 비교 가능한 튜플로 변환. '3.12.12' -> (3, 12, 12)"""
    parts = []
    for part in v.split("."):
        # 숫자만 뽑기 (혹시 '3.12.0rc1' 같은 게 있으면)
        num_str = ""
        for ch in part:
            if ch.isdigit():
                num_str += ch
            else:
                break
        parts.append(int(num_str) if num_str else 0)
    return tuple(parts)


def find_matching(constraint: str) -> PythonInstall | None:
    """
    버전 제약("3.12", "3.12.5" 등)에 맞는 파이썬 찾기.
    "3.12"면 3.12.x 아무거나 매칭.
    """
    installs = detect_all()
    constraint_tuple = _version_tuple(constraint)

    for install in installs:
        install_tuple = _version_tuple(install.version)
        # 제약 길이만큼만 앞부분 비교
        if install_tuple[:len(constraint_tuple)] == constraint_tuple:
            return install

    return None