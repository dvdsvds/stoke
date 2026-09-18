"""
스캐폴딩 중 필요한 툴(go, cargo, dotnet, composer 등)이 시스템에 없을 때,
그냥 "없다"고 경고만 하고 넘어가는 대신 stoke의 기존 프로젝트-로컬 설치
메커니즘(`stoke install <language>`, 전역 상태 안 건드림)으로 그 자리에서
설치할지 물어보기 위한 공용 헬퍼.

모든 언어가 대상은 아님 -- stoke가 직접 설치해줄 수 있는 건 SUPPORTED_LANGUAGES에
있는 것뿐이고(Kotlin은 여기 없음: Kotlin 컴파일러는 Gradle이 직접 관리하고
stoke는 JDK만 설치해주는 구조라, "gradle이 없다"는 문제 자체를 이 메커니즘으로는
못 고침 -- kotlin/*.py는 이 헬퍼를 안 씀).
"""
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
    """.stoke/toolchains/<language>-*/ 밑에서 exe_name을 재귀적으로 찾음
    (언어마다 압축 내부 레이아웃이 달라서 정확한 서브패스 대신 이름으로 탐색)."""
    toolchain_dir = _find_toolchain_dir(project_path, language)
    if toolchain_dir is None:
        return None
    for match in toolchain_dir.rglob(exe_name):
        if match.is_file():
            return match
    return None

def _prompt_and_install(language: str, project_path: Path, display_name: str, exe_name: str) -> bool:
    """설치할지 물어보고, 승낙하면 `stoke install <language>`를 이 프로젝트 안에서 실행.
    설치를 시도했으면(성공/실패 무관) True, 사용자가 거절했으면 False."""
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
    """
    exe_names(POSIX 이름, 필요하면 (posix, windows) 튜플)가 PATH나 프로젝트
    로컬 툴체인에 있으면 그 경로를 반환. 없으면 `stoke install <language>`로
    지금 설치할지 물어보고, 승낙하면 설치 후 새로 생긴 실행파일 경로를 찾아 반환.
    거절하거나 설치 실패하면 None (호출부가 기존처럼 수동 안내로 폴백).
    """
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
    """
    cargo 전용 버전의 ensure_tool. rustup으로 설치된 cargo는 실제 컴파일러로
    넘겨주는 얇은 프록시라서 RUSTUP_HOME/CARGO_HOME을 함께 알려줘야 동작함
    (rust/adapter.py의 _find_cargo()와 동일한 로직) -- 그래서 실행파일 경로만
    돌려주는 ensure_tool()로는 부족해 별도로 둠.
    반환: (cargo_exe_path, env) 또는 (설치 안 했으면) None.
    """
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
    """
    bundle 전용 버전의 ensure_tool. `stoke install ruby`는 ruby 자체만 설치하고
    Bundler는 별도 gem이라 보장이 안 됨 -- 그래서 ruby를 먼저 설치/확인한 다음,
    그 ruby 옆에 bundle이 없으면 그 ruby의 gem으로 `gem install bundler`까지 해줌.
    """
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
