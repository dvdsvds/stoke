"""설치된 Rust 툴체인 감지 (rustup 있으면 그걸로, 없으면 rustc 하나만)."""
import subprocess
import shutil
from dataclasses import dataclass

@dataclass
class RustInstall:
    channel: str           # rust-toolchain.toml에 쓸 짧은 이름: "stable", "nightly", "1.75.0" 등
    exact_version: str      # 표시용 정확한 버전 (예: "1.90.0"), 모르면 channel과 동일
    is_default: bool = False

def _run(args: list[str]) -> str | None:
    try:
        result = subprocess.run(args, capture_output=True, text=True, errors="replace", timeout=5)
        if result.returncode == 0:
            return result.stdout
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    return None

def _host_triple() -> str | None:
    """rustc -vV의 'host:' 줄에서 현재 시스템 타겟 트리플을 얻음 (rustup 툴체인 이름에서 떼어내기용)."""
    output = _run(["rustc", "-vV"])
    if not output:
        return None
    for line in output.splitlines():
        if line.startswith("host:"):
            return line.split(":", 1)[1].strip()
    return None

def _exact_version(toolchain: str | None) -> str | None:
    """`rustc [+toolchain] --version` 출력에서 버전 숫자만 뽑음 (예: "rustc 1.90.0 (...)" -> "1.90.0")."""
    args = ["rustc"] + ([f"+{toolchain}"] if toolchain else []) + ["--version"]
    output = _run(args)
    if not output:
        return None
    parts = output.strip().split()
    return parts[1] if len(parts) >= 2 else None

def _detect_via_rustup() -> list[RustInstall]:
    if shutil.which("rustup") is None:
        return []
    output = _run(["rustup", "toolchain", "list"])
    if not output:
        return []

    host = _host_triple()
    installs = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("no installed toolchains"):
            continue
        is_default = line.endswith("(default)")
        name = line.replace("(default)", "").strip()

        channel = name
        if host and channel.endswith(f"-{host}"):
            channel = channel[: -(len(host) + 1)]

        exact = _exact_version(name) or channel
        installs.append(RustInstall(channel=channel, exact_version=exact, is_default=is_default))
    return installs

def _detect_via_rustc() -> list[RustInstall]:
    """rustup 없이 rustc만 있는 경우 (예: 배포판 패키지로 설치)."""
    if shutil.which("rustc") is None:
        return []
    version = _exact_version(None)
    if not version:
        return []
    return [RustInstall(channel=version, exact_version=version, is_default=True)]

def detect_all() -> list[RustInstall]:
    """설치된 Rust 툴체인 목록 (rustup 우선, 없으면 rustc 하나). 못 찾으면 빈 리스트."""
    installs = _detect_via_rustup()
    if installs:
        return installs
    return _detect_via_rustc()
