import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

@dataclass
class JavaInstall:
    version: str          # 예: "21.0.1"
    major_version: int    # 예: 21
    java_home: Path       # JDK 루트 폴더
    javac: Path           # javac 실행파일 경로
    java: Path            # java 실행파일 경로
    is_default: bool = False

def _get_javac_version(javac_path: str) -> str | None:
    """javac -version 실행해서 버전 문자열 얻기."""
    try:
        result = subprocess.run(
            [javac_path, "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # javac는 stderr로 버전 출력하는 경우가 있음 (Java 8 이하)
        # 최신은 stdout으로 출력
        output = (result.stdout + result.stderr).strip()
        # 출력 예시:
        #   "javac 21.0.1"
        #   "javac 1.8.0_301"
        if output.startswith("javac "):
            return output[len("javac "):].strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    return None

def _parse_major_version(version: str) -> int:
    """
    버전 문자열에서 메이저 버전 추출.
    "21.0.1" -> 21
    "1.8.0_301" -> 8 (Java 8은 1.8로 표기)
    "17" -> 17
    """
    parts = version.split(".")
    if not parts:
        return 0

    first = parts[0]
    # 숫자만 뽑기
    num_str = ""
    for ch in first:
        if ch.isdigit():
            num_str += ch
        else:
            break

    if not num_str:
        return 0

    major = int(num_str)

    # Java 8 이하: "1.8.0_xxx" 형태 -> 실제 메이저는 8
    if major == 1 and len(parts) >= 2:
        second_num = ""
        for ch in parts[1]:
            if ch.isdigit():
                second_num += ch
            else:
                break
        if second_num:
            return int(second_num)

    return major

def _find_javac_in(java_home: Path) -> Path | None:
    """JAVA_HOME 안에서 javac 실행파일 찾기."""
    candidates = [
        java_home / "bin" / "javac.exe",   # 윈도우
        java_home / "bin" / "javac",       # 리눅스/맥
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None

def _find_java_in(java_home: Path) -> Path | None:
    """JAVA_HOME 안에서 java 실행파일 찾기."""
    candidates = [
        java_home / "bin" / "java.exe",
        java_home / "bin" / "java",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None

def _detect_via_java_home() -> JavaInstall | None:
    """JAVA_HOME 환경변수로 JDK 감지."""
    java_home_str = os.environ.get("JAVA_HOME")
    if not java_home_str:
        return None

    java_home = Path(java_home_str)
    if not java_home.is_dir():
        return None

    javac = _find_javac_in(java_home)
    java = _find_java_in(java_home)
    if javac is None or java is None:
        return None

    version = _get_javac_version(str(javac))
    if version is None:
        return None

    return JavaInstall(
        version=version,
        major_version=_parse_major_version(version),
        java_home=java_home,
        javac=javac,
        java=java,
        is_default=True,   # JAVA_HOME 지정된 건 사용자 명시적 선택이라 default
    )

def _detect_via_path() -> JavaInstall | None:
    """PATH에서 javac 찾기."""
    javac_str = shutil.which("javac")
    if javac_str is None:
        return None

    javac = Path(javac_str).resolve()

    # javac가 있는 폴더의 부모가 보통 JAVA_HOME
    # 예: /c/Program Files/Java/jdk-21/bin/javac.exe -> java_home = /c/Program Files/Java/jdk-21
    java_home = javac.parent.parent

    java = _find_java_in(java_home)
    if java is None:
        return None

    version = _get_javac_version(str(javac))
    if version is None:
        return None

    return JavaInstall(
        version=version,
        major_version=_parse_major_version(version),
        java_home=java_home,
        javac=javac,
        java=java,
        is_default=True,
    )

def _detect_via_common_paths() -> list[JavaInstall]:
    """
    표준 JDK 설치 경로들을 스캔해서 발견된 JDK 목록 반환.
    Windows/Linux/macOS 모두 대응.
    """
    import sys

    candidate_bases = []

    if sys.platform == "win32":
        # Windows 표준 JDK 설치 위치
        candidate_bases = [
            Path("C:/Program Files/Eclipse Adoptium"),
            Path("C:/Program Files/Java"),
            Path("C:/Program Files/Zulu"),
            Path("C:/Program Files/Amazon Corretto"),
            Path("C:/Program Files/Microsoft"),
        ]
    elif sys.platform == "darwin":
        # macOS
        candidate_bases = [
            Path("/Library/Java/JavaVirtualMachines"),
        ]
    else:
        # Linux
        candidate_bases = [
            Path("/usr/lib/jvm"),
            Path("/opt/java"),
        ]

    installs = []
    for base in candidate_bases:
        if not base.exists():
            continue
        try:
            for entry in base.iterdir():
                if not entry.is_dir():
                    continue

                # macOS는 Contents/Home 밑에 실제 JDK
                if sys.platform == "darwin":
                    java_home = entry / "Contents" / "Home"
                else:
                    java_home = entry

                javac = _find_javac_in(java_home)
                java = _find_java_in(java_home)
                if javac is None or java is None:
                    continue

                version = _get_javac_version(str(javac))
                if version is None:
                    continue

                major = _parse_major_version(version)
                installs.append(JavaInstall(
                    version=version,
                    major_version=major,
                    java_home=java_home,
                    javac=javac,
                    java=java,
                    is_default=False,
                ))
        except (OSError, PermissionError):
            continue

    return installs

def detect_all() -> list[JavaInstall]:
    """설치된 모든 JDK 감지."""
    installs = []
    seen_homes: set[Path] = set()
    # 1. JAVA_HOME 우선
    from_env = _detect_via_java_home()
    if from_env is not None:
        seen_homes.add(from_env.java_home.resolve())
        installs.append(from_env)
    # 2. PATH 스캔 (JAVA_HOME이랑 다르면 추가)
    from_path = _detect_via_path()
    if from_path is not None:
        resolved = from_path.java_home.resolve()
        if resolved not in seen_homes:
            seen_homes.add(resolved)
            from_path.is_default = len(installs) == 0
            installs.append(from_path)
    # 3. 표준 경로 스캔 (이미 발견되지 않은 것만 추가)
    for install in _detect_via_common_paths():
        resolved = install.java_home.resolve()
        if resolved not in seen_homes:
            seen_homes.add(resolved)
            install.is_default = len(installs) == 0
            installs.append(install)
    return installs

def find_matching(constraint: str) -> JavaInstall | None:
    """
    버전 제약("21", "17.0.1")에 맞는 JDK 찾기.
    "21"이면 major 버전 21 매칭.
    """
    installs = detect_all()

    # 숫자만 있는 경우 (예: "21") -> 메이저 버전 매칭
    try:
        target_major = int(constraint)
        for install in installs:
            if install.major_version == target_major:
                return install
        return None
    except ValueError:
        pass

    # 정확한 버전 매칭 (예: "21.0.1")
    for install in installs:
        if install.version == constraint:
            return install

    # prefix 매칭 (예: "21.0" -> "21.0.1" OK)
    for install in installs:
        if install.version.startswith(constraint + "."):
            return install

    return None