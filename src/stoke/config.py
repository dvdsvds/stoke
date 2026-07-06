import tomllib
from dataclasses import dataclass, field
from pathlib import Path


# 데이터 클래스: 설정 파일 내용
@dataclass
class ProjectInfo:
    name: str
    version: str
    lock_mode: str = "commit"  # "commit" 또는 "local"

@dataclass
class Target:
    name: str
    language: str
    sources: list[str] = field(default_factory=list)
    entry: str | None = None
    deps: dict[str, str] = field(default_factory=dict)
    python_version: str | None = None
    java_version: str | None = None
    main_class: str | None = None
    c_standard: str | None = None
    cpp_standard: str | None = None
    includes: list[str] = field(default_factory=list)

@dataclass
class Config:
    project: ProjectInfo
    targets: dict[str, Target]
    config_path: Path  # stoke.toml 파일 위치 (나중에 상대 경로 처리에 필요)


# stoke.toml 파일 찾기: 현재 → 상위 → 상위 → ... 로 올라감
def find_config_file(start_dir: Path | None = None) -> Path:
    if start_dir is None:
        start_dir = Path.cwd()

    current = start_dir.resolve()

    # 루트 디렉토리 만날 때까지 상위로 올라가면서 찾기
    while True:
        candidate = current / "stoke.toml"
        if candidate.exists():
            return candidate

        # 루트에 도달했는데도 못 찾음
        if current.parent == current:
            raise FileNotFoundError(
                f"stoke.toml not found in {start_dir} or any parent directory"
            )

        current = current.parent


# ============================================================
# 설정 파일 파싱 + 검증
# ============================================================

def load_config(config_path: Path | None = None) -> Config:
    if config_path is None:
        config_path = find_config_file()

    # tomllib은 바이너리 모드로 열어야 함 (표준 규약)
    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    # [project] 섹션 검증
    if "project" not in data:
        raise ValueError(f"Missing [project] section in {config_path}")

    project_data = data["project"]
    if "name" not in project_data:
        raise ValueError(f"Missing 'name' in [project] section")

    project = ProjectInfo(
        name=project_data["name"],
        version=project_data.get("version", "0.0.0"),
        lock_mode=project_data.get("lock_mode", "commit"),
    )

    # [targets.*] 섹션들 파싱
    targets = {}
    targets_data = data.get("targets", {})

    for target_name, target_config in targets_data.items():
        if "language" not in target_config:
            raise ValueError(
                f"Missing 'language' in [targets.{target_name}]"
            )

    targets[target_name] = Target(
        name=target_name,
        language=target_config["language"],
        sources=target_config.get("sources", []),
        entry=target_config.get("entry"),
        deps=target_config.get("deps", {}),
        python_version=target_config.get("python_version"),
        java_version=target_config.get("java_version"),
        main_class=target_config.get("main_class"),
        c_standard=target_config.get("c_standard"),
        cpp_standard=target_config.get("cpp_standard"),
        includes=target_config.get("includes", []),
    )

    if not targets:
        raise ValueError(f"No targets defined in {config_path}")

    return Config(
        project=project,
        targets=targets,
        config_path=config_path,
    )