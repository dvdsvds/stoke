"""stoke install --language=X --version=Y 명령어."""
import sys
import subprocess
import urllib.request
import tempfile
import zipfile
import shutil
from pathlib import Path
from stoke.install_versions import fetch_versions, find_version, get_platform_key
from stoke.http_utils import basic_auth_headers
from stoke.config import find_config_file

SUPPORTED_LANGUAGES = (
    "python", "java", "c", "cpp", "conda", "go", "nodejs",
    "rust", "kotlin", "csharp", "ruby", "php",
)

def _toolchains_dir(project_root: Path) -> Path:
    """언어 툴체인 설치 폴더 반환. 프로젝트 로컬(.stoke/toolchains) — 전역 캐시 없음.
    프로젝트를 지우면 같이 지워지고, PC에 언어별 잔여 캐시가 남지 않음."""
    return project_root / ".stoke" / "toolchains"

def _find_project_root() -> Path:
    """stoke.toml 위치를 현재 디렉토리부터 상위로 탐색해서 프로젝트 루트 반환."""
    try:
        return find_config_file().parent
    except FileNotFoundError:
        print("Error: stoke.toml not found in this directory or any parent.", file=sys.stderr)
        print("stoke install downloads languages into the current project's .stoke/ folder —", file=sys.stderr)
        print("run it from inside a project created with 'stoke init'.", file=sys.stderr)
        sys.exit(1)

def cmd_install_language(language: str, version: str, base_url: str | None = None):
    """
    stoke install --language=[language name] --version=[version] [--base-url=<url>]

    언어는 현재 프로젝트의 .stoke/toolchains/ 안에 설치됨 (전역 설치 없음, PATH 변경 없음).
    stoke build/run이 stoke.toml의 버전 지정을 보고 이 경로를 직접 찾아 씀.

    base_url: 버전 메타데이터를 가져올 base URL 오버라이드.
    안 주면 STOKE_VERSION_API_BASE 환경변수 또는 stoke 기본 엔드포인트 사용.
    사내망에서 dvdsvds.github.io에 못 닿을 때, 같은 JSON 스키마로 미러링한
    사내 서버를 가리키기 위함.
    """
    # 지원 언어 및 환경 확인
    if language not in SUPPORTED_LANGUAGES:
        print(f"Error: unsupported language '{language}'", file=sys.stderr)
        print(f"Supported: {', '.join(SUPPORTED_LANGUAGES)}", file=sys.stderr)
        sys.exit(1)

    project_root = _find_project_root()

    # c/cpp는 gcc 툴체인 사용
    api_language = "gcc" if language in ("c", "cpp") else language

    # 버전 목록 조회
    print(f"Fetching {api_language} versions...")
    try:
        versions_data = fetch_versions(api_language, base_url=base_url)
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
        _install_windows(installer_path, api_language, version_info["version"], project_root)
    elif sys.platform == "darwin":
        _install_macos(installer_path)
    else:
        print("Error: Linux installation not supported yet", file=sys.stderr)
        sys.exit(1)


def _download(url: str) -> Path:
    """URL에서 파일 다운로드. 임시 파일 경로 반환. (사설 미러가 인증을 요구하면
    STOKE_VERSION_API_USER/PASSWORD로 Basic Auth 헤더를 붙임.)"""
    filename = url.split("/")[-1]
    tmp_dir = Path(tempfile.gettempdir())
    dest = tmp_dir / filename

    from stoke.install_versions import get_version_api_credentials
    user, password = get_version_api_credentials()
    req = urllib.request.Request(url, headers=basic_auth_headers(user, password))

    with urllib.request.urlopen(req, timeout=30) as response:
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

def _registry_key_path(major_minor: str) -> str:
    return f"Software\\Python\\PythonCore\\{major_minor}"

def _registry_key_exists(major_minor: str) -> bool:
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _registry_key_path(major_minor)):
            return True
    except FileNotFoundError:
        return False

def _delete_registry_tree(path: str) -> None:
    """path와 그 하위 키 전부 삭제. winreg에 재귀 삭제가 없어서 직접 순회."""
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
    except FileNotFoundError:
        return
    subkeys = []
    with key:
        i = 0
        while True:
            try:
                subkeys.append(winreg.EnumKey(key, i))
                i += 1
            except OSError:
                break
    for sub in subkeys:
        _delete_registry_tree(f"{path}\\{sub}")
    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)

def _install_windows(installer_path: Path, language: str = None, version: str = None, project_root: Path = None):
    """Windows installer 실행. .exe / .msi / .zip / .7z 지원.
    전부 프로젝트의 .stoke/toolchains/ 안으로 설치되고 PATH는 건드리지 않음 —
    stoke build/run이 stoke.toml에 pin된 버전을 보고 이 경로를 직접 찾아 씀."""
    suffix = installer_path.suffix.lower()
    dest = _toolchains_dir(project_root) / f"{language}-{version}"

    if language == "rust":
        _install_rust(installer_path, dest, version)
        print(f"\n{language} {version} installed to: {dest}")
        _print_local_hint(dest)
        return

    if suffix == ".msi":
        # MSI: msiexec으로 dest에 조용히 설치, PATH 등록 안 함
        print(f"Installing to {dest}...")
        dest.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                ["msiexec", "/i", str(installer_path), "/passive",
                 f"TARGETDIR={dest}", f"INSTALLDIR={dest}"],
                check=False,
            )
        except FileNotFoundError:
            print(f"Error: installer not found: {installer_path}", file=sys.stderr)
            sys.exit(1)
        print(f"\n{language} {version} installed to: {dest}")
        _print_local_hint(dest)

    elif suffix == ".exe":
        # python.org 공식 인스톨러: TargetDir로 설치 위치 지정, PrependPath=0으로 전역 PATH 등록 방지.
        # 그래도 HKCU\Software\Python\PythonCore\<major.minor>에는 무조건 자기 자신을
        # 등록해버려서 (py 런처가 이걸로 찾음), 원래 그 버전이 등록돼 있지 않았다면
        # 설치 후 그 레지스트리 흔적을 지운다 — 안 그러면 프로젝트를 지워도 죽은 경로가
        # 레지스트리에 남고, 다른 프로젝트가 이걸 "시스템 파이썬"으로 오인할 수 있음.
        major_minor = ".".join(version.split(".")[:2])
        existed_before = _registry_key_exists(major_minor) if language == "python" else False

        print(f"Installing to {dest}...")
        dest.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                [str(installer_path), "/passive",
                 f"TargetDir={dest}", "PrependPath=0", "Include_launcher=0",
                 "InstallAllUsers=0"],
                check=False,
            )
        except FileNotFoundError:
            print(f"Error: installer not found: {installer_path}", file=sys.stderr)
            sys.exit(1)

        if language == "python":
            if existed_before:
                print(
                    f"Warning: Python {major_minor} was already registered system-wide "
                    f"(py launcher); this install just overwrote that registration.\n"
                    f"  Reinstall Python {major_minor} normally if you need the old registration back."
                )
            else:
                _delete_registry_tree(_registry_key_path(major_minor))

        print(f"\n{language} {version} installed to: {dest}")
        _print_local_hint(dest)

    elif suffix == ".zip":
        # Zip: 파이썬 zipfile로 압축 해제
        _extract_zip(installer_path, dest)
        if language == "python":
            _bootstrap_embeddable_python(dest)
        print(f"\n{language} {version} installed to: {dest}")
        _print_local_hint(dest)

    elif suffix == ".7z":
        # 7z: 7-Zip 사용
        _extract_7z(installer_path, dest)
        print(f"\n{language} {version} installed to: {dest}")
        _print_local_hint(dest)

    else:
        print(f"Error: unsupported installer format: {suffix}", file=sys.stderr)
        sys.exit(1)

def _extract_zip(zip_path: Path, dest: Path) -> None:
    """.zip 파일을 dest에 압축 해제."""
    print(f"Extracting to {dest}...")
    dest.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(dest)
    except zipfile.BadZipFile as e:
        print(f"Error: invalid zip file: {e}", file=sys.stderr)
        sys.exit(1)

def _extract_7z(archive_path: Path, dest: Path) -> None:
    """.7z 파일을 dest에 압축 해제. py7zr(순수 파이썬)을 써서 외부 7-Zip 설치가 필요 없음."""
    import py7zr

    print(f"Extracting to {dest}...")
    dest.mkdir(parents=True, exist_ok=True)

    try:
        with py7zr.SevenZipFile(archive_path, mode="r") as archive:
            archive.extractall(path=dest)
    except py7zr.exceptions.Bad7zFile as e:
        print(f"Error: invalid 7z file: {e}", file=sys.stderr)
        sys.exit(1)

def _install_rust(rustup_init: Path, dest: Path, version: str) -> None:
    """
    Rust는 gcc/nodejs처럼 미리 빌드된 xcopy용 zip이 없음 — 공식 배포는 rustc/cargo/std
    등을 각자 따로 압축한 "컴포넌트" 묶음이라 rustup 없이 직접 조립하기 어려움.
    대신 rustup-init.exe를 RUSTUP_HOME/CARGO_HOME이 프로젝트의 .stoke/toolchains/ 안을
    가리키게 해서 돌리면, rustup 자체가 그 안에만 설치되고 전역 ~/.rustup, ~/.cargo,
    PATH는 전혀 안 건드림.
    """
    rustup_home = dest / "rustup"
    cargo_home = dest / "cargo"
    dest.mkdir(parents=True, exist_ok=True)

    import os
    env = dict(os.environ)
    env["RUSTUP_HOME"] = str(rustup_home)
    env["CARGO_HOME"] = str(cargo_home)

    print(f"Installing to {dest}...")
    result = subprocess.run(
        [str(rustup_init), "-y", "--no-modify-path",
         "--default-toolchain", version, "--profile", "minimal"],
        env=env,
        capture_output=True, text=True, errors="replace",
    )
    if result.returncode != 0:
        print(f"Error: rustup-init failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

def _bootstrap_embeddable_python(dest: Path) -> None:
    """
    python.org의 embeddable zip 배포판은 pip/venv가 빠져 있음 (기본적으로
    site-packages도 비활성화). MSI 인스톨러 방식은 같은 버전을 여러 프로젝트가
    동시에 로컬 설치하려 하면 Windows Installer가 "이미 설치됨"으로 보고 조용히
    실패하는 문제가 있어서, 순수 파일 복사만으로 끝나는 embeddable을 쓰는 대신
    직접 pip/virtualenv를 심어준다.

    1. python3XX._pth에 site-packages 활성화
    2. get-pip.py로 pip 부트스트랩
    3. venv 모듈이 없으므로 pip으로 virtualenv 패키지 설치
       (stdlib venv와 달리 ensurepip 없이도 동작하도록 만들어진 패키지라 여기서 씀)
    """
    python_exe = dest / "python.exe"
    pth_files = list(dest.glob("python3*._pth"))
    if not python_exe.exists() or not pth_files:
        print(f"Warning: unexpected embeddable layout in {dest}, skipping pip bootstrap.")
        return

    pth_file = pth_files[0]
    content = pth_file.read_text(encoding="utf-8")
    if "Lib\\site-packages" not in content:
        content += "\nLib\\site-packages\n"
    content = content.replace("#import site", "import site")
    pth_file.write_text(content, encoding="utf-8")

    print("Bootstrapping pip into embeddable Python...")
    get_pip = dest / "get-pip.py"
    req = urllib.request.Request("https://bootstrap.pypa.io/get-pip.py")
    with urllib.request.urlopen(req, timeout=30) as response:
        get_pip.write_bytes(response.read())

    result = subprocess.run(
        [str(python_exe), str(get_pip), "--no-warn-script-location"],
        capture_output=True, text=True, errors="replace",
    )
    get_pip.unlink(missing_ok=True)
    if result.returncode != 0:
        print(f"Warning: pip bootstrap failed:\n{result.stderr}", file=sys.stderr)
        return

    print("Installing virtualenv (replaces stdlib venv, which embeddable Python lacks)...")
    result = subprocess.run(
        [str(python_exe), "-m", "pip", "install", "virtualenv", "--no-warn-script-location"],
        capture_output=True, text=True, errors="replace",
    )
    if result.returncode != 0:
        print(f"Warning: virtualenv install failed:\n{result.stderr}", file=sys.stderr)
        return

    (dest / ".stoke-embeddable").write_text("", encoding="utf-8")

def _print_local_hint(dest: Path) -> None:
    print(f"No PATH changes needed - stoke build/run picks this up automatically")
    print(f"when stoke.toml requests this version.")

def _install_macos(installer_path: Path):
    """macOS 파이썬 installer 실행."""
    print(f"Opening installer: {installer_path}")
    print("Please follow the installer wizard.")
    subprocess.run(["open", str(installer_path)], check=False)
    print("After installation, run 'stoke python list' to verify.")

def cmd_list_language_versions(language: str, base_url: str | None = None):
    """stoke install --language=X --list [--base-url=<url>]"""
    if language not in SUPPORTED_LANGUAGES:
        print(f"Error: unsupported language '{language}'", file=sys.stderr)
        sys.exit(1)

    # c/cpp는 gcc 툴체인 사용
    api_language = "gcc" if language in ("c", "cpp") else language

    print(f"Fetching {api_language} versions...")
    try:
        versions_data = fetch_versions(api_language, base_url=base_url)
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
    if language not in SUPPORTED_LANGUAGES:
        print(f"Error: unsupported language '{language}'", file=sys.stderr)
        sys.exit(1)

    api_language = "gcc" if language in ("c", "cpp") else language

    project_root = _find_project_root()
    toolchains = _toolchains_dir(project_root)
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