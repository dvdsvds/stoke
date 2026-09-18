"""스캐폴딩 중 툴(go, cargo, dotnet 등)이 없으면 `stoke install`로 그 자리에서 설치할지 물어보는 헬퍼."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from stoke.prompts import _prompt_yes_no

def _find_toolchain_dir(project_path: Path, language: str) -> Path | None:
    """.stoke/toolchains/<language>-*/ 중 가장 최근(이름 역순 정렬) 것."""
    toolchains = project_path / ".stoke" / "toolchains"
    if not toolchains.is_dir():
        return None
    dirs = sorted(toolchains.glob(f"{language}-*"), reverse=True)
    return dirs[0] if dirs else None

def _find_toolchain_exe(project_path: Path, language: str, exe_name: str) -> Path | None:
    """.stoke/toolchains/<language>-*/ 밑에서 exe_name을 재귀적으로 찾음."""
    toolchain_dir = _find_toolchain_dir(project_path, language)
    if toolchain_dir is None:
        return None
    for match in toolchain_dir.rglob(exe_name):
        if match.is_file():
            return match
    return None

def _prompt_and_install(language: str, project_path: Path, display_name: str, exe_name: str) -> bool:
    """설치할지 물어보고, 승낙하면 `stoke install <language>` 실행. 시도했으면 True, 거절하면 False."""
    if not _prompt_yes_no(f"'{exe_name}' not found. Install {display_name} into this project now?", default=True):
        return False

    prev_cwd = Path.cwd()
    try:
        os.chdir(project_path)
        from stoke.cli.install_lang import cmd_install_language
        try:
            cmd_install_language(language, "latest")
        except SystemExit:
            pass
    finally:
        os.chdir(prev_cwd)
    return True

def ensure_tool(
    language: str,
    exe_names: str | tuple[str, str],
    project_path: Path,
    display_name: str | None = None,
) -> str | None:
    """PATH/로컬 툴체인에서 exe_names 찾기, 없으면 설치 제안 후 재탐색 (거절/실패 시 None)."""
    if isinstance(exe_names, tuple):
        posix_name, windows_name = exe_names
    else:
        posix_name = windows_name = exe_names
    exe_name = windows_name if sys.platform == "win32" else posix_name

    found = shutil.which(exe_name)
    if found:
        return found

    local = _find_toolchain_exe(project_path, language, exe_name)
    if local:
        return str(local)

    if not _prompt_and_install(language, project_path, display_name or exe_name, exe_name):
        return None

    local = _find_toolchain_exe(project_path, language, exe_name)
    return str(local) if local else None

def ensure_cargo(project_path: Path) -> tuple[str, dict] | None:
    """cargo 전용 ensure_tool -- RUSTUP_HOME/CARGO_HOME도 같이 반환해야 해서 별도로 둠."""
    exe_name = "cargo.exe" if sys.platform == "win32" else "cargo"

    found = shutil.which("cargo")
    if found:
        return found, dict(os.environ)

    def _local_cargo() -> tuple[str, dict] | None:
        toolchain_dir = _find_toolchain_dir(project_path, "rust")
        if toolchain_dir is None:
            return None
        cargo_exe = toolchain_dir / "cargo" / "bin" / exe_name
        if not cargo_exe.is_file():
            return None
        env = dict(os.environ)
        env["RUSTUP_HOME"] = str(toolchain_dir / "rustup")
        env["CARGO_HOME"] = str(toolchain_dir / "cargo")
        return str(cargo_exe), env

    local = _local_cargo()
    if local:
        return local

    if not _prompt_and_install("rust", project_path, "Rust", exe_name):
        return None

    return _local_cargo()

def ensure_bundle(project_path: Path) -> str | None:
    """bundle 전용 ensure_tool -- ruby 먼저 확보한 뒤, 없으면 그 gem으로 bundler 설치."""
    bundle_name = "bundle.bat" if sys.platform == "win32" else "bundle"
    ruby_name = "ruby.exe" if sys.platform == "win32" else "ruby"
    gem_name = "gem.bat" if sys.platform == "win32" else "gem"

    found = shutil.which(bundle_name) or _find_toolchain_exe(project_path, "ruby", bundle_name)
    if found:
        return str(found)

    ruby_exe = ensure_tool("ruby", (ruby_name, ruby_name), project_path, display_name="Ruby")
    if not ruby_exe:
        return None

    found = shutil.which(bundle_name) or _find_toolchain_exe(project_path, "ruby", bundle_name)
    if found:
        return str(found)

    gem_exe = Path(ruby_exe).parent / gem_name
    if not gem_exe.is_file():
        which_gem = shutil.which("gem")
        if not which_gem:
            return None
        gem_exe = Path(which_gem)

    print("Installing Bundler gem...")
    result = subprocess.run(
        [str(gem_exe), "install", "bundler", "--no-document"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Warning: gem install bundler failed:\n{result.stderr}", file=sys.stderr)
        return None

    found = shutil.which(bundle_name) or _find_toolchain_exe(project_path, "ruby", bundle_name)
    return str(found) if found else None
