"""Rust 어댑터: carge build/run 위임"""
import subprocess
import shutil
import sys
import tomllib
from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.config import Target, ProjectInfo

class RustAdapter(BaseAdapter):
    def __init__(
        self, 
        target: Target, 
        project: ProjectInfo, 
        project_root: Path, 
        verbose: bool = False
    ):
        super().__init__(target, project, project_root, verbose=verbose)
        self.build_dir = project_root / ".stoke" / "rust" / target.name
        self.manifest_path = self._resolve_manifest_path()
        self.package_name = self._read_package_name()
        bin_name = self.package_name + (".exe" if self._is_windows() else "")
        self.output_path = self.build_dir / "release" / bin_name

    @staticmethod
    def _is_windows() -> bool:
        return sys.platform == "win32"

    def _resolve_manifest_path(self) -> Path:
        """
        사용할 Cargo.toml 경로.

        <target.name>/Cargo.toml이 있으면 그걸 씀 (Cargo 워크스페이스 멤버,
        멀티 타겟 프로젝트 구조 -- 루트 Cargo.toml의 [workspace] members에
        이 디렉토리가 등록돼 있다고 가정). 없으면 프로젝트 루트의 Cargo.toml
        (기존 단일 타겟 프로젝트, 하위 호환). --manifest-path로 명시하면
        워크스페이스 루트가 아니라 멤버 디렉토리에서 실행해도 그 멤버만
        정확히 빌드됨 (Cargo.lock/의존성 해석은 여전히 워크스페이스 전체 기준).
        """
        member_manifest = self.project_root / self.target.name / "Cargo.toml"
        if member_manifest.is_file():
            return member_manifest
        return self.project_root / "Cargo.toml"

    def _read_package_name(self) -> str:
        """Cargo.toml의 [package] name 읽기. 없으면 타겟 이름 사용"""
        if not self.manifest_path.exists():
            return self.target.name
        try:
            with open(self.manifest_path, "rb") as f:
                data = tomllib.load(f)
            return data.get("package", {}).get("name", self.target.name)
        except(tomllib.TOMLDecodeError, OSError):
            return self.target.name

    def _find_cargo(self) -> str:
        """cargo 실행파일 경로 찾기"""
        cargo_exe = shutil.which("cargo")
        if cargo_exe is None:
            raise RuntimeError(
                "cargo not found in PATH.\n"
                "  Install Rust from: https://rustup.rs"
            )
        return cargo_exe

    def build(self, force: bool = False) -> None:
        """cargo build -- release로 빌드. (cargo 자체가 증분 빌드를 캐싱하므로 force는 별도 처리 안 함)"""
        cargo_exe = self._find_cargo()

        result = subprocess.run(
            [cargo_exe, "--version"],
            capture_output=True,
            text=True,
            errors="replace",
        )

        if result.returncode == 0:
            print(f"Using {result.stdout.strip()}")

        self.build_dir.mkdir(parents=True, exist_ok=True)
        print(f"Building 'cargo build --release --manifest-path {self.manifest_path}' -> {self.output_path}")

        cmd = [
            cargo_exe, "build",
            "--release",
            "--manifest-path", str(self.manifest_path),
            "--target-dir", str(self.build_dir),
        ]
        result = subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            errors="replace",
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"cargo build failed:\n{result.stderr}"
            )

        self._ensure_gitignore()
        print(f"Build complete: {self.target.name}")

    def run(self) -> int:
        """빌드된 바이너리 실행"""
        if not self.output_path.exists():
            raise RuntimeError(
                f"Executable not found: {self.output_path}\n"
                f"  Run 'stoke build' first."
            )
        print(f"Running; {self.output_path}\n")
        try:
            result = subprocess.run([str(self.output_path)])
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        """hot-reload용 실행 명령어"""
        if not self.output_path.exists():
            raise RuntimeError(
                f"Executable not found: {self.output_path}\n"
                f"  Run 'stoke build' first."
            )
        return [str(self.output_path)]

    def _gitignore_entries(self) -> list[str]:
        return [".stoke/", "target/"]
