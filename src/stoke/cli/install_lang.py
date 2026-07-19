"""stoke install --language=X --version=Y 명령어."""
import sys
import subprocess
import urllib.request
import tempfile
from pathlib import Path

from stoke.install_versions import fetch_versions, find_version, get_platform_key


def cmd_install_language(language: str, version: str):
    """
    stoke install --language=python --version=3.12
    """
    # 지원 언어 확인
    if language not in ("python",):
        print(f"Error: unsupported language '{language}'", file=sys.stderr)
        print(f"Supported: python", file=sys.stderr)
        sys.exit(1)

    # 버전 목록 조회
    print(f"Fetching {language} versions...")
    try:
        versions_data = fetch_versions(language)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 요청 버전 찾기
    version_info = find_version(versions_data, version)
    if version_info is None:
        print(f"Error: version '{version}' not found for {language}", file=sys.stderr)
        print(f"Available versions:", file=sys.stderr)
        for v in versions_data.get("versions", []):
            print(f"  {v['version']}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {language} {version_info['version']} (released {version_info.get('released', 'unknown')})")

    # 플랫폼 확인
    platform_key = get_platform_key()
    download_url = version_info.get("downloads", {}).get(platform_key)
    if not download_url:
        print(f"Error: no download available for {platform_key}", file=sys.stderr)
        print(f"Try installing manually from python.org", file=sys.stderr)
        sys.exit(1)

    # 다운로드
    print(f"Downloading from {download_url}...")
    try:
        installer_path = _download(download_url)
    except Exception as e:
        print(f"Error: download failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Downloaded to {installer_path}")

    # 설치 실행
    if sys.platform == "win32":
        _install_windows(installer_path)
    elif sys.platform == "darwin":
        _install_macos(installer_path)
    else:
        print("Error: Linux installation not supported yet", file=sys.stderr)
        sys.exit(1)


def _download(url: str) -> Path:
    """URL에서 파일 다운로드. 임시 파일 경로 반환."""
    filename = url.split("/")[-1]
    tmp_dir = Path(tempfile.gettempdir())
    dest = tmp_dir / filename

    with urllib.request.urlopen(url, timeout=30) as response:
        total = int(response.headers.get("Content-Length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    pct = downloaded * 100 // total
                    print(f"  {pct}% ({downloaded // 1024} KB / {total // 1024} KB)", end="\r")
        print()

    return dest


def _install_windows(installer_path: Path):
    """Windows 파이썬 installer 실행."""
    print(f"Running installer: {installer_path}")
    print("Installer will open. Follow the wizard.")

    try:
        # /passive: 최소 UI, /norestart: 재시작 안 함
        result = subprocess.run(
            [str(installer_path), "/passive", "PrependPath=1"],
            check=False,
        )
        if result.returncode == 0:
            print("Installation complete.")
            print("Run 'stoke python list' to verify.")
        else:
            print(f"Installer exited with code {result.returncode}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: installer not found: {installer_path}", file=sys.stderr)
        sys.exit(1)


def _install_macos(installer_path: Path):
    """macOS 파이썬 installer 실행."""
    print(f"Opening installer: {installer_path}")
    print("Please follow the installer wizard.")
    subprocess.run(["open", str(installer_path)], check=False)
    print("After installation, run 'stoke python list' to verify.")