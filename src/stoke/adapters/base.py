from abc import ABC, abstractmethod
from pathlib import Path

from stoke.config import ProjectInfo, Target


class BaseAdapter(ABC):
    """
    모든 언어 어댑터의 공통 인터페이스.
    각 언어별 구현은 이 클래스를 상속받아 build()를 구현해야 함.
    """

    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
    ):
        self.target = target
        self.project = project
        self.project_root = project_root

    @abstractmethod
    def build(self, force: bool = False) -> None:
        """
        빌드 실행. 진짜 진입점.
        force=True면 캐시 무시하고 전체 재빌드.
        실패 시 RuntimeError 발생.
        """
        pass

    def run(self) -> int:
        """
        빌드된 타겟 실행. 반환: 종료 코드.
        기본 구현은 지원 안 함 에러. 어댑터가 오버라이드.
        """
        raise RuntimeError(
            f"'stoke run' is not supported for language '{self.target.language}'"
        )

    def get_run_command(self) -> list[str]:
        """
        서브프로세스로 실행할 명령어 리스트 반환.
        hot-reload와 같이 프로세스 관리가 필요한 곳에서 사용.
        기본 구현은 지원 안 함 에러. 어댑터가 오버라이드.
        """
        raise RuntimeError(
            f"Running as subprocess is not supported for language '{self.target.language}'"
        )

    def _ensure_gitignore(self) -> None:
        """
        .stoke/ 를 .gitignore에 자동 추가.
        모든 언어 공통이라 여기 둠.
        """
        gitignore_path = self.project_root / ".gitignore"

        needed_entries = [".stoke/"]
        # 언어별 IDE 파일 추가
        if self.target.language == "java":
            needed_entries.extend([".classpath", ".project", "pom.xml"])
        elif self.target.language in ("c", "cpp"):
            needed_entries.extend(["compile_commands.json", ".vscode/c_cpp_properties.json"])

        existing = ""
        if gitignore_path.exists():
            existing = gitignore_path.read_text(encoding="utf-8")

        existing_lines = set(
            line.strip() for line in existing.splitlines() if line.strip()
        )

        added = []
        for entry in needed_entries:
            if entry not in existing_lines:
                added.append(entry)

        if added:
            has_stoke_header = "# Added by stoke" in existing
            with open(gitignore_path, "a", encoding="utf-8") as f:
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                if not has_stoke_header:
                    if existing:
                        f.write("\n# Added by stoke\n")
                    else:
                        f.write("# Added by stoke\n")
                for entry in added:
                    f.write(f"{entry}\n")
            print(f"Updated .gitignore: added {', '.join(added)}")