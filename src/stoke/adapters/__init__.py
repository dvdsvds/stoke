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
) -> BaseAdapter:
    """
    language에 맞는 어댑터를 생성해서 반환.
    지원하지 않는 언어면 RuntimeError.
    profile: C/C++만 사용 (Python/Java는 무시).
    """
    if target.language == "python":
        from stoke.adapters.python import PythonAdapter
        return PythonAdapter(target, project, project_root)
    if target.language == "java":
        from stoke.adapters.java import JavaAdapter
        return JavaAdapter(target, project, project_root)
    if target.language == "c":
        from stoke.adapters.c import CAdapter
        return CAdapter(target, project, project_root, profile=profile)
    if target.language == "cpp":
        from stoke.adapters.cpp import CppAdapter
        return CppAdapter(target, project, project_root, profile=profile)

    raise RuntimeError(
        f"Unsupported language: '{target.language}'\n"
        f"  Currently supported: python, java, c, cpp"
    )