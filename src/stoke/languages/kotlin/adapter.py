"""Kotlin 어댑터: Gradle build/run 위임."""
import subprocess
import shutil
import sys
from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.config import Target, ProjectInfo

class KotlinAdapter(BaseAdapter):
    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        super().__init__(target, project, project_root, verbose=verbose)
        self.build_dir = project_root / "build"

    @staticmethod
    def _is_windows() -> bool:
        return sys.platform == "win32"

    def _find_gradle(self) -> list[str]:
        """
        Gradle 실행 명령어 찾기.
        프로젝트에 Gradle Wrapper(gradlew)가 있으면 그걸 우선 사용, 없으면 시스템 gradle.
        """
        wrapper_name = "gradlew.bat" if self._is_windows() else "gradlew"
        wrapper_path = self.project_root / wrapper_name
        if wrapper_path.exists():
            return [str(wrapper_path)]

        gradle_exe = shutil.which("gradle")
        if gradle_exe:
            return [gradle_exe]

        raise RuntimeError(
            "Neither Gradle wrapper (gradlew) nor system 'gradle' found.\n"
            "  Run 'gradle wrapper' in the project, or install Gradle: https://gradle.org/install"
        )

    def _print_jdk_info(self) -> None:
        """감지된 JDK 정보 출력 (참고용, 빌드에는 Gradle 자체 툴체인 사용)."""
        from stoke.languages.java.versions import detect_all as detect_java
        installs = detect_java()
        for install in installs:
            if install.is_default:
                print(f"Using JDK {install.version} ({install.java_home})")
                return
        if installs:
            print(f"Using JDK {installs[0].version} ({installs[0].java_home})")

    def build(self, force: bool = False) -> None:
        """gradlew build로 빌드."""
        gradle_cmd = self._find_gradle()
        self._print_jdk_info()

        print("Building 'gradle build'...")

        cmd = gradle_cmd + ["build", "-x", "test"]
        if force:
            cmd.append("--rerun-tasks")
        result = subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"gradle build failed:\n{result.stdout}\n{result.stderr}"
            )

        self._ensure_gitignore()
        print(f"Build complete: {self.target.name}")

    def run(self) -> int:
        """Gradle Application 플러그인으로 실행 (build.gradle.kts에 'application' 필요)."""
        gradle_cmd = self._find_gradle()
        cmd = gradle_cmd + ["run", "-q", "--console=plain"]

        print("Running: gradle run\n")
        try:
            result = subprocess.run(cmd, cwd=str(self.project_root))
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        """hot-reload용 실행 명령어."""
        gradle_cmd = self._find_gradle()
        return gradle_cmd + ["run", "-q", "--console=plain"]

    def _gitignore_entries(self) -> list[str]:
        return [".stoke/", "build/", ".gradle/"]
