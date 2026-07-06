"""
VSCode .vscode/settings.json 관리.
프로젝트별 IDE 설정 자동 생성/병합.
"""

import json
from pathlib import Path


# stoke가 관리하는 키 목록 (프로젝트 폴더 settings.json)
STOKE_MANAGED_KEYS_PROJECT = {
    # 자바
    "java.project.referencedLibraries",
    # 파이썬
    "python.defaultInterpreterPath",
    "python.analysis.extraPaths",
    # 공통
    "files.exclude",
}


def _load_existing(path: Path) -> dict:
    """기존 settings.json 로드. 없거나 파싱 실패 시 빈 dict."""
    if not path.exists():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        # VSCode settings.json은 주석을 허용하지만 표준 JSON은 아님
        # 간단히 표준 JSON으로 처리 (주석 있으면 실패 시 빈 dict 반환)
        return json.loads(text)
    except (json.JSONDecodeError, OSError):
        return {}


def _merge_stoke_keys(existing: dict, stoke_config: dict) -> dict:
    """
    기존 설정을 유지하면서 stoke 관리 키만 갱신.
    stoke 관리 키가 stoke_config에 없으면 기존 값 유지.
    """
    result = dict(existing)
    for key, value in stoke_config.items():
        result[key] = value
    return result


def write_project_settings(
    project_root: Path,
    settings: dict,
) -> Path:
    """
    프로젝트 폴더의 .vscode/settings.json 생성/병합.
    반환: 저장된 파일 경로.
    """
    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    settings_path = vscode_dir / "settings.json"
    existing = _load_existing(settings_path)
    merged = _merge_stoke_keys(existing, settings)

    settings_path.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return settings_path


def make_java_settings(jar_files: list[Path], project_root: Path) -> dict:
    """
    자바 프로젝트용 VSCode 설정.
    referencedLibraries: 외부 JAR 목록을 VSCode Java 확장이 인식하도록.
    """
    lib_paths = []
    for jar in jar_files:
        try:
            rel = jar.relative_to(project_root)
            lib_paths.append(str(rel).replace("\\", "/"))
        except ValueError:
            lib_paths.append(str(jar).replace("\\", "/"))

    return {
        "java.project.referencedLibraries": lib_paths,
    }


def make_python_settings(venv_python: Path, project_root: Path) -> dict:
    """
    파이썬 프로젝트용 VSCode 설정.
    ${workspaceFolder} 상대 경로로 표현.
    """
    try:
        rel = venv_python.relative_to(project_root)
        interpreter_path = "${workspaceFolder}/" + str(rel).replace("\\", "/")
    except ValueError:
        interpreter_path = str(venv_python).replace("\\", "/")

    return {
        "python.defaultInterpreterPath": interpreter_path,
    }

# 재귀 스캔 시 제외할 폴더들
EXCLUDED_DIRS = {
    ".stoke",
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "target",   # Rust/Java Maven 관례
    "build",
    "dist",
    ".idea",
    ".vscode",
}


def find_stoke_projects(root: Path) -> list[Path]:
    """
    root 아래에서 stoke.toml이 있는 폴더들을 재귀 탐색.
    EXCLUDED_DIRS는 스캔 안 함.
    반환: stoke.toml이 있는 폴더 경로 리스트.
    """
    projects = []

    def walk(current: Path):
        # 현재 폴더에 stoke.toml 있으면 등록
        if (current / "stoke.toml").is_file():
            projects.append(current)
            # stoke 프로젝트 발견하면 그 하위는 스캔 안 함
            # (프로젝트 안에 다른 프로젝트가 있는 경우는 드물고,
            #  있어도 별도로 관리하는 게 나음)
            return

        # 하위 폴더 탐색
        try:
            for entry in current.iterdir():
                if not entry.is_dir():
                    continue
                if entry.name in EXCLUDED_DIRS:
                    continue
                walk(entry)
        except (OSError, PermissionError):
            pass

    walk(root)
    return projects


def make_workspace_settings(projects_by_language: dict) -> dict:
    """
    워크스페이스 루트용 VSCode 설정.
    projects_by_language: {"java": [Path, ...], "python": [Path, ...]}
    """
    settings = {}

    # 자바: rootPaths에 상대 경로 배열
    if "java" in projects_by_language and projects_by_language["java"]:
        java_paths = []
        for project_path in projects_by_language["java"]:
            java_paths.append(str(project_path).replace("\\", "/"))
        settings["java.project.rootPaths"] = java_paths

    # 파이썬은 워크스페이스 레벨에서 단일 인터프리터만 지원
    # 여러 개면 첫 번째만 기본으로 설정
    if "python" in projects_by_language and projects_by_language["python"]:
        first_project_abs = projects_by_language["python"][0]["absolute"]
        # 상대 경로로
        first_project_rel = projects_by_language["python"][0]["relative"]
        venv_python_rel = f"{first_project_rel}/.stoke/python/{first_project_rel.name}/venv/bin/python.exe"
        settings["python.defaultInterpreterPath"] = f"${{workspaceFolder}}/{venv_python_rel}"

    return settings