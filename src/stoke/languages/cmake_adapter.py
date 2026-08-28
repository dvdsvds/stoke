"""build_system = "cmake" 어댑터. stoke 자체 컴파일 모델 대신 cmake configure+build로 위임.

c_standard/cpp_standard/profiles의 compile_flags/defines는 CMakeLists.txt가 관리하는
영역이라 여기서는 안 씀 -- 표준/컴파일 플래그를 바꾸려면 CMakeLists.txt를 고쳐야 함.
profile은 CMAKE_BUILD_TYPE(Debug/Release) 매핑에만 씀.
"""
import shutil
import subprocess
import sys
from pathlib import Path

from stoke.adapters.base import BaseAdapter

_BUILD_TYPE_MAP = {"debug": "Debug", "release": "Release"}

def _executable_name(name: str) -> str:
    import platform
    return f"{name}.exe" if platform.system() == "Windows" else name

def _safe_print(text: str, **kwargs) -> None:
    """cmake 출력엔 콘솔 코드페이지로 인코딩 못 하는 문자가 섞일 수 있어서
    (Windows cp949 콘솔에서 재현됨), 실패하면 대체 문자로 바꿔서 다시 출력."""
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        print(text.encode(encoding, errors="replace").decode(encoding), **kwargs)

class CMakeAdapter(BaseAdapter):
    def __init__(self, target, project, project_root: Path, profile=None, verbose: bool = False):
        super().__init__(target, project, project_root, verbose=verbose)
        self.profile = profile
        profile_name = profile.name if profile else "default"
        self.source_path = project_root / target.source_dir
        self.build_dir = project_root / ".stoke" / "cmake" / target.name / profile_name
        self.output_path: Path | None = None

    def _build_type(self) -> str:
        return _BUILD_TYPE_MAP.get(self.profile.name if self.profile else "debug", "Debug")

    def _find_executable(self) -> Path | None:
        """빌드 디렉토리에서 타겟 이름과 일치하는 실행 파일 탐색 (가장 최근 수정된 것 우선)."""
        wanted = _executable_name(self.target.name)
        matches = [p for p in self.build_dir.rglob(wanted) if p.is_file()]
        if not matches:
            return None
        return max(matches, key=lambda p: p.stat().st_mtime)

    def build(self, force: bool = False) -> None:
        cmake = shutil.which("cmake")
        if cmake is None:
            raise RuntimeError(
                "cmake not found in PATH.\n"
                "  Install CMake: https://cmake.org/download/"
            )

        cmakelists = self.source_path / "CMakeLists.txt"
        if not cmakelists.exists():
            raise RuntimeError(f"CMakeLists.txt not found: {cmakelists}")

        if force and self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True, exist_ok=True)

        print(f"Configuring '{self.target.name}' with CMake ({self._build_type()})...")
        configure_cmd = [
            cmake, "-S", str(self.source_path), "-B", str(self.build_dir),
            f"-DCMAKE_BUILD_TYPE={self._build_type()}",
        ]
        proc = subprocess.run(configure_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if self.verbose and proc.stdout:
            _safe_print(proc.stdout)
        if proc.returncode != 0:
            raise RuntimeError(f"cmake configure failed:\n{proc.stderr.strip() or proc.stdout.strip()}")

        print(f"Building '{self.target.name}'...")
        build_cmd = [cmake, "--build", str(self.build_dir), "--config", self._build_type()]
        if self.project.jobs:
            build_cmd.extend(["--parallel", str(self.project.jobs)])
        proc = subprocess.run(build_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.stdout:
            _safe_print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
        if proc.returncode != 0:
            raise RuntimeError(f"cmake build failed:\n{proc.stderr.strip()}")

        self.output_path = self._find_executable()
        self._ensure_gitignore()
        print(f"\nBuild complete: {self.target.name}")

    def run(self) -> int:
        if self.output_path is None:
            self.output_path = self._find_executable()
        if self.output_path is None:
            raise RuntimeError(
                f"No executable named '{_executable_name(self.target.name)}' found under {self.build_dir}\n"
                f"  Run 'stoke build' first, and make sure the CMake target produces an executable with that name."
            )
        print(f"Running: {self.output_path}\n")
        try:
            result = subprocess.run([str(self.output_path)])
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        if self.output_path is None:
            self.output_path = self._find_executable()
        if self.output_path is None:
            raise RuntimeError(
                f"No executable named '{_executable_name(self.target.name)}' found under {self.build_dir}\n"
                f"  Run 'stoke build' first."
            )
        return [str(self.output_path)]

    def _gitignore_entries(self) -> list[str]:
        return [".stoke/"]
