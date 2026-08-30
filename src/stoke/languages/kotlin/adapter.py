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

    def _task_path(self, task: str) -> str:
        """
        Gradle 태스크 경로. <target.name>/build.gradle.kts가 있으면 그 서브프로젝트로
        범위를 좁힘 (":<target.name>:<task>") -- Gradle 멀티 프로젝트 빌드에서
        여러 모듈을 include()해둔 구조. 없으면 루트 프로젝트 자기 자신으로만 범위를
        좁힘 (":<task>").

        콜론을 꼭 붙이는 이유: 콜론 없이 그냥 "<task>"만 주면 Gradle이 그 이름의
        태스크를 가진 *모든* 서브프로젝트에서 전부 실행해버림 (멀티 프로젝트
        빌드에서의 기본 동작) -- 이러면 stoke build worker가 다른 타겟까지
        같이 빌드해버려서 진짜 독립적인 타겟이 아니게 됨.
        """
        subproject_build_gradle = self.project_root / self.target.name / "build.gradle.kts"
        if subproject_build_gradle.is_file():
            return f":{self.target.name}:{task}"
        return f":{task}"

    def _resolve_java_home(self) -> Path | None:
        """
        stoke.toml의 java_version에 맞는 JDK 찾기.
        java_version이 없으면 시스템 기본 JDK 정보만 출력하고 None 반환
        (이 경우 Gradle 자체 툴체인 해석에 맡김).
        java_version이 있는데 맞는 JDK가 없으면 에러.
        """
        from stoke.languages.java.versions import detect_all as detect_java, find_matching

        if not self.target.java_version:
            installs = detect_java()
            for install in installs:
                if install.is_default:
                    print(f"Using JDK {install.version} ({install.java_home})")
                    return None
            if installs:
                print(f"Using JDK {installs[0].version} ({installs[0].java_home})")
            return None

        install = find_matching(self.target.java_version)
        if install is None:
            available = detect_java()
            available_versions = ", ".join(str(i.major_version) for i in available)
            raise RuntimeError(
                f"stoke.toml requests JDK {self.target.java_version}, but it's not installed on this system.\n"
                f"  Available versions: {available_versions or '(none)'}\n"
                f"  Install JDK {self.target.java_version}, or update java_version in stoke.toml."
            )
        print(f"Using JDK {install.version} ({install.java_home}) - pinned via java_version in stoke.toml")
        return install.java_home

    def _java_home_args(self) -> list[str]:
        """java_version에 맞는 JDK가 있으면 -Dorg.gradle.java.home으로 강제."""
        java_home = self._resolve_java_home()
        if java_home is None:
            return []
        return [f"-Dorg.gradle.java.home={java_home}"]

    def build(self, force: bool = False) -> None:
        """gradlew build로 빌드."""
        gradle_cmd = self._find_gradle()
        java_home_args = self._java_home_args()
        build_task = self._task_path("build")
        test_task = self._task_path("test")

        print(f"Building 'gradle {build_task}'...")

        cmd = gradle_cmd + java_home_args + [build_task, "-x", test_task]
        if force:
            cmd.append("--rerun-tasks")
        result = subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            errors="replace",
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
        run_task = self._task_path("run")
        cmd = gradle_cmd + self._java_home_args() + [run_task, "-q", "--console=plain"]

        print(f"Running: gradle {run_task}\n")
        try:
            result = subprocess.run(cmd, cwd=str(self.project_root))
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def get_run_command(self) -> list[str]:
        """hot-reload용 실행 명령어."""
        gradle_cmd = self._find_gradle()
        run_task = self._task_path("run")
        return gradle_cmd + self._java_home_args() + [run_task, "-q", "--console=plain"]

    def test(self, verbose: bool = False) -> int:
        """gradle test 실행 (build에서는 -x로 빼둔 태스크를 여기서 돌림)."""
        gradle_cmd = self._find_gradle()
        test_task = self._task_path("test")
        cmd = gradle_cmd + self._java_home_args() + [test_task]
        if verbose:
            cmd.append("--info")
        print(f"Running: gradle {test_task}\n")
        try:
            result = subprocess.run(cmd, cwd=str(self.project_root))
            return result.returncode
        except KeyboardInterrupt:
            return 130

    def _gitignore_entries(self) -> list[str]:
        return [".stoke/", "build/", ".gradle/"]
