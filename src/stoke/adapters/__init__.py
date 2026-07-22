from pathlib import Path

from stoke.adapters.base import BaseAdapter
from stoke.config import ProjectInfo, Target

from pathlib import Path
from stoke.adapters.base import BaseAdapter
from stoke.config import ProjectInfo, Target, Profile

def make_adapter(
    target: Target,
    project: ProjectInfo,
    project_root: Path,
    profile: Profile | None = None,
    verbose: bool = False,
) -> BaseAdapter:
    """
    language에 맞는 어댑터를 생성해서 반환.
    지원하지 않는 언어면 RuntimeError.
    profile: C/C++만 사용 (Python/Java는 무시).
    verbose: 상세 로그 출력 여부.
    """
    if target.language == "python":
        from stoke.languages.python.adapter import PythonAdapter
        return PythonAdapter(target, project, project_root, verbose=verbose)
    if target.language == "java":
        from stoke.languages.java.adapter import JavaAdapter
        return JavaAdapter(target, project, project_root, verbose=verbose)
    if target.language == "c":
        from stoke.languages.c.adapter import CAdapter
        return CAdapter(target, project, project_root, profile=profile, verbose=verbose)
    if target.language == "cpp":
        from stoke.languages.cpp.adapter import CppAdapter
        return CppAdapter(target, project, project_root, profile=profile, verbose=verbose)
    if target.language == "go":
        from stoke.languages.go.adapter import GoAdapter
        return GoAdapter(target, project, project_root, verbose=verbose)