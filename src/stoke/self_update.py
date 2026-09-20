"""stoke self-update -- 실행 중인 standalone 배포판(PyInstaller onedir)을 최신 릴리스로 교체.

pip install -e . 등으로 소스에서 직접 실행 중이면(= frozen이 아니면) 의미가 없어서 에러로 거부함.
"""
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from stoke import __version__

_RELEASES_API = "https://api.github.com/repos/dvdsvds/stoke/releases/latest"
_USER_AGENT = "stoke-self-update"

class UpdateInfo:
    def __init__(self, version: str, assets: dict[str, str]):
        self.version = version  # "2.4.0" (v 없이)
        self.assets = assets    # {asset_name: download_url}

def _parse_version(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split(".") if p.isdigit())

def is_frozen() -> bool:
    """PyInstaller onedir 빌드로 실행 중인지 (소스/pip install -e 실행이면 False)."""
    return bool(getattr(sys, "frozen", False))

def fetch_latest(timeout: int = 15) -> UpdateInfo:
    req = urllib.request.Request(
        _RELEASES_API, headers={"User-Agent": _USER_AGENT, "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read())
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error checking for updates: {getattr(e, 'reason', e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error checking for updates: {e}")

    tag = data.get("tag_name", "")
    version = tag[1:] if tag.startswith("v") else tag
    assets = {a["name"]: a["browser_download_url"] for a in data.get("assets", [])}
    return UpdateInfo(version=version, assets=assets)

def is_newer(latest: str, current: str) -> bool:
    return _parse_version(latest) > _parse_version(current)

def _platform_asset_name(version: str) -> str | None:
    system = platform.system()
    if system == "Windows":
        return f"stoke-setup-{version}.exe"
    machine = platform.machine().lower()
    arch = "x86_64" if machine in ("x86_64", "amd64") else machine
    plat = "macos" if system == "Darwin" else "linux" if system == "Linux" else None
    if plat is None:
        return None
    return f"stoke-{version}-{plat}-{arch}.tar.gz"

def _download(url: str, dest: Path, timeout: int = 60) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response, open(dest, "wb") as f:
        shutil.copyfileobj(response, f)

def _install_dir() -> Path:
    """현재 실행 중인 stoke 바이너리가 들어있는 디렉토리 (PyInstaller onedir 배포 루트)."""
    return Path(sys.executable).resolve().parent

def apply_update_unix(url: str, install_dir: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        archive = tmp_path / "stoke.tar.gz"
        _download(url, archive)

        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()
        with tarfile.open(archive) as tf:
            for member in tf.getmembers():
                member_path = (extract_dir / member.name).resolve()
                if not str(member_path).startswith(str(extract_dir.resolve())):
                    raise RuntimeError(f"Refusing to extract unsafe archive member: {member.name}")
            tf.extractall(extract_dir)

        new_root = extract_dir / "stoke"
        if not new_root.is_dir() or not (new_root / "stoke").is_file():
            raise RuntimeError("Downloaded archive doesn't look like a stoke release (missing stoke/stoke)")

        backup_dir = install_dir.parent / f"{install_dir.name}.old"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        install_dir.rename(backup_dir)
        try:
            shutil.move(str(new_root), str(install_dir))
            exe = install_dir / "stoke"
            exe.chmod(exe.stat().st_mode | 0o111)
        except Exception:
            if install_dir.exists():
                shutil.rmtree(install_dir)
            backup_dir.rename(install_dir)
            raise
        shutil.rmtree(backup_dir, ignore_errors=True)

def apply_update_windows(url: str) -> None:
    # mkdtemp (TemporaryDirectory 아님) -- 설치 프로그램이 이 exe를 계속 읽는 동안 우리가
    # 먼저 종료돼서 정리할 기회가 없음. 임시 파일 하나 남는 건 감수.
    tmp = Path(tempfile.mkdtemp(prefix="stoke-self-update-"))
    installer = tmp / "stoke-setup.exe"
    _download(url, installer)
    # 현재 프로세스가 끝나기 전에 설치 프로그램을 떼어내 백그라운드로 실행 -- 설치 파일들이
    # 잠겨있지 않아야 덮어쓸 수 있어서, 호출부가 이 함수 직후 바로 종료해야 함.
    subprocess.Popen(
        [str(installer), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
    )
