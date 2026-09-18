from abc import ABC, abstractmethod
from pathlib import Path

from stoke.config import ProjectInfo, Target

class BaseAdapter(ABC):
    """모든 언어 어댑터의 공통 인터페이스. 서브클래스는 build()를 구현해야 함."""

    def __init__(
        self,
        target: Target,
        project: ProjectInfo,
        project_root: Path,
        verbose: bool = False,
    ):
        self.target = target
        self.project = project
        self.project_root = project_root
        self.verbose = verbose

    @abstractmethod
    def build(self, force: bool = False) -> None:
        """빌드 실행 (force=True면 캐시 무시하고 전체 재빌드, 실패 시 RuntimeError)."""
        pass

    def run(self) -> int:
        """빌드된 타겟 실행. 반환: 종료 코드 (기본 구현은 미지원 에러, 어댑터가 오버라이드)."""
        raise RuntimeError(
            f"'stoke run' is not supported for language '{self.target.language}'"
        )

    def get_run_command(self) -> list[str]:
        """서브프로세스로 실행할 명령어 리스트 반환 (hot-reload 등에서 사용, 기본은 미지원 에러)."""
        raise RuntimeError(
            f"Running as subprocess is not supported for language '{self.target.language}'"
        )

    def test(self, verbose: bool = False) -> int:
        """타겟의 테스트 실행. 반환: 종료 코드 (기본 구현은 미지원 에러)."""
        raise RuntimeError(
            f"'stoke test' is not supported for language '{self.target.language}'"
        )

    def _ensure_gitignore(self) -> None:
        """.stoke/ 를 .gitignore에 자동 추가 (모든 언어 공통)."""
        gitignore_path = self.project_root / ".gitignore"

        needed_entries = self._gitignore_entries()

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

    def _gitignore_entries(self) -> list[str]:
        """이 어댑터가 .gitignore에 넣고 싶은 항목들 (서브클래스가 오버라이드)."""
        entries = [".stoke/"]
        ide = self.project.ide
        if self.target.language == "java":
            if ide == "eclipse":
                entries.extend([".classpath", ".project"])
            elif ide == "intellij":
                entries.append("pom.xml")
        elif self.target.language in ("c", "cpp"):
            if ide in ("vscode", "intellij"):
                entries.append("compile_commands.json")
            if ide == "vscode":
                entries.append(".vscode/c_cpp_properties.json")
        return entries