"""stoke install --language=X --version=Y 명령어."""
import sys
import subprocess
import urllib.request
import tempfile
import zipfile
import shutil
import os
from pathlib import Path
from stoke.install_versions import fetch_versions, find_version, get_platform_key

def _toolchains_dir() -> Path:
    """언어 툴체인 설치 폴더 반환."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
        return base / "Programs" / "stoke" / "toolchains"
    else:
        return Path.home() / ".stoke" / "toolchains"

def cmd_install_language(language: str, version: str):
    """
    stoke install --language=[language name] --version=[version]
    """
    # 지원 언어 및 환경 확인
    if language not in ("python", "java", "c", "cpp", "conda", "go", "nodejs"):
        print(f"Error: unsupported language '{language}'", file=sys.stderr)
        print(f"Supported: python, java, c, cpp, conda, go", file=sys.stderr)
        sys.exit(1)

    # c/cpp는 gcc 툴체인 사용
    api_language = "gcc" if language in ("c", "cpp") else language

    # 버전 목록 조회
    print(f"Fetching {api_language} versions...")
    try:
        versions_data = fetch_versions(api_language)
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
        _install_windows(installer_path, api_language, version_info["version"])
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

def _install_windows(installer_path: Path, language: str = None, version: str = None):
    """Windows installer 실행. .exe / .msi / .zip / .7z 지원."""
    suffix = installer_path.suffix.lower()

    if suffix == ".msi":
        # MSI: msiexec 사용
        print(f"Running installer: {installer_path}")
        print("Installer will open. Follow the wizard.")
        try:
            subprocess.run(
                ["msiexec", "/i", str(installer_path), "/passive"],
                check=False,
            )
        except FileNotFoundError:
            print(f"Error: installer not found: {installer_path}", file=sys.stderr)
            sys.exit(1)

    elif suffix == ".exe":
        # EXE: 그대로 실행
        print(f"Running installer: {installer_path}")
        print("Installer will open. Follow the wizard.")
        try:
            subprocess.run(
                [str(installer_path), "/passive", "PrependPath=1"],
                check=False,
            )
        except FileNotFoundError:
            print(f"Error: installer not found: {installer_path}", file=sys.stderr)
            sys.exit(1)

    elif suffix == ".zip":
        # Zip: 파이썬 zipfile로 압축 해제
        _extract_zip(installer_path, language, version)

    elif suffix == ".7z":
        # 7z: 7-Zip 사용
        _extract_7z(installer_path, language, version)

    else:
        print(f"Error: unsupported installer format: {suffix}", file=sys.stderr)
        sys.exit(1)

def _extract_zip(zip_path: Path, language: str, version: str) -> None:
    """.zip 파일 압축 해제."""
    dest = _toolchains_dir() / f"{language}-{version}"
    print(f"Extracting to {dest}...")
    dest.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(dest)
    except zipfile.BadZipFile as e:
        print(f"Error: invalid zip file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{language} {version} installed to: {dest}")
    _print_path_hint(dest, language)

def _extract_7z(archive_path: Path, language: str, version: str) -> None:
    """.7z 파일 압축 해제. 7-Zip 필요."""
    seven_zip = shutil.which("7z")
    if seven_zip is None:
        print("Error: 7-Zip is required to extract .7z archives.", file=sys.stderr)
        print("Install from: https://www.7-zip.org/", file=sys.stderr)
        print(f"Downloaded archive: {archive_path}", file=sys.stderr)
        sys.exit(1)

    dest = _toolchains_dir() / f"{language}-{version}"
    print(f"Extracting to {dest}...")
    dest.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [seven_zip, "x", str(archive_path), f"-o{dest}", "-y"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error: 7-Zip extraction failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{language} {version} installed to: {dest}")
    _print_path_hint(dest, language)

def _print_path_hint(dest: Path, language: str) -> None:
    """PATH 안내 출력."""
    if language == "go":
        bin_path = dest / "go" / "bin"
    elif language in ("c", "cpp", "gcc"):
        candidates = list(dest.glob("*/bin"))
        bin_path = candidates[0] if candidates else dest / "bin"
    elif language == "nodejs":
        # Node.js는 압축 풀면 node-vXX-win-x64/ 폴더 안에 node.exe 있음
        candidates = [d for d in dest.iterdir() if d.is_dir() and d.name.startswith("node-")]
        bin_path = candidates[0] if candidates else dest
    else:
        bin_path = dest / "bin"

    print(f"\nTo use, add this to PATH:")
    print(f"  {bin_path}")

def _install_macos(installer_path: Path):
    """macOS 파이썬 installer 실행."""
    print(f"Opening installer: {installer_path}")
    print("Please follow the installer wizard.")
    subprocess.run(["open", str(installer_path)], check=False)
    print("After installation, run 'stoke python list' to verify.")

def cmd_list_language_versions(language: str):
    """stoke install --language=X --list"""
    if language not in ("python", "java", "c", "cpp", "conda", "go", "nodejs"):
        print(f"Error: unsupported language '{language}'", file=sys.stderr)
        sys.exit(1)

    # c/cpp는 gcc 툴체인 사용
    api_language = "gcc" if language in ("c", "cpp") else language

    print(f"Fetching {api_language} versions...")
    try:
        versions_data = fetch_versions(api_language)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"\nAvailable {language} versions:")
    for v in versions_data.get("versions", []):
        released = v.get("released", "unknown")
        print(f"  {v['version']}  (released {released})")
    print()
    print(f"Install: stoke install --language={language} --version=<version>")

def cmd_uninstall_language(language: str, version: str = None):
    """stoke uninstall --language=X --version=Y"""
    if language not in ("python", "java", "c", "cpp", "conda", "go"):
        print(f"Error: unsupported language '{language}'", file=sys.stderr)
        sys.exit(1)

    api_language = "gcc" if language in ("c", "cpp") else language

    toolchains = _toolchains_dir()
    if not toolchains.exists():
        print(f"No stoke-installed toolchains found at: {toolchains}", file=sys.stderr)
        sys.exit(1)

    # 설치된 버전 찾기
    prefix = f"{api_language}-"
    installed = [d for d in toolchains.iterdir() if d.is_dir() and d.name.startswith(prefix)]

    if not installed:
        print(f"No stoke-installed {language} found.", file=sys.stderr)
        sys.exit(1)

    # 버전 지정 안 하면 목록 표시
    if version is None:
        print(f"Installed {language} versions:")
        for d in installed:
            v = d.name[len(prefix):]
            print(f"  {v}")
        print()
        print(f"Usage: stoke uninstall --language={language} --version=<version>")
        return

    # 특정 버전 삭제
    target_dir = toolchains / f"{api_language}-{version}"
    if not target_dir.exists():
        print(f"Error: {language} {version} not found in {toolchains}", file=sys.stderr)
        print(f"Installed versions:", file=sys.stderr)
        for d in installed:
            v = d.name[len(prefix):]
            print(f"  {v}", file=sys.stderr)
        sys.exit(1)

    # 확인 프롬프트
    print(f"Delete {language} {version}?")
    print(f"  Path: {target_dir}")
    print(f"Confirm? [y/N]: ", end="")
    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if answer != "y":
        print("Cancelled.")
        return

    # 삭제
    try:
        shutil.rmtree(target_dir)
    except OSError as e:
        print(f"Error: cannot delete: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Uninstalled {language} {version}.")
    print(f"Note: You may need to remove the path from PATH manually.")