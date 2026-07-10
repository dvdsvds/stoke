import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileStat:
    mtime: float
    size: int

@dataclass
class TargetCache:
    # 문법 체크 캐시: 파일 경로(문자열) -> FileStat
    syntax_check: dict[str, FileStat] = field(default_factory=dict)
    # C/C++ 헤더 의존성 캐시: 소스 파일 경로 -> {헤더 경로: FileStat}
    header_deps: dict[str, dict[str, FileStat]] = field(default_factory=dict)

@dataclass
class BuildCache:
    targets: dict[str, TargetCache] = field(default_factory=dict)

    def get_target(self, target_name: str) -> TargetCache:
        """타겟 캐시 가져오기. 없으면 새로 생성."""
        if target_name not in self.targets:
            self.targets[target_name] = TargetCache()
        return self.targets[target_name]

def _cache_path(project_root: Path) -> Path:
    return project_root / ".stoke" / "cache.json"

def load_cache(project_root: Path) -> BuildCache:
    """캐시 파일 읽기. 없거나 손상되면 빈 캐시 반환."""
    path = _cache_path(project_root)
    if not path.exists():
        return BuildCache()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        # 손상된 캐시는 그냥 무시하고 빈 캐시로
        return BuildCache()

    cache = BuildCache()
    targets_data = data.get("targets", {})
    for target_name, target_data in targets_data.items():
        target_cache = TargetCache()
        syntax_data = target_data.get("syntax_check", {})
        for file_path, stat_data in syntax_data.items():
            target_cache.syntax_check[file_path] = FileStat(
                mtime=stat_data["mtime"],
                size=stat_data["size"],
            )
        # 헤더 의존성 캐시 파싱
        header_data = target_data.get("header_deps", {})
        for src_path, headers_data in header_data.items():
            headers = {}
            for header_path, stat_data in headers_data.items():
                headers[header_path] = FileStat(
                    mtime=stat_data["mtime"],
                    size=stat_data["size"],
                )
            target_cache.header_deps[src_path] = headers
        cache.targets[target_name] = target_cache
    return cache

def save_cache(project_root: Path, cache: BuildCache) -> None:
    """캐시 파일 쓰기."""
    path = _cache_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {"targets": {}}
    for target_name, target_cache in cache.targets.items():
        syntax_data = {}
        for file_path, stat in target_cache.syntax_check.items():
            syntax_data[file_path] = {
                "mtime": stat.mtime,
                "size": stat.size,
            }
        # 헤더 의존성 저장
        header_data = {}
        for src_path, headers in target_cache.header_deps.items():
            headers_data = {}
            for header_path, stat in headers.items():
                headers_data[header_path] = {
                    "mtime": stat.mtime,
                    "size": stat.size,
                }
            header_data[src_path] = headers_data
        data["targets"][target_name] = {
            "syntax_check": syntax_data,
            "header_deps": header_data,
        }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_file_stat(path: Path) -> FileStat:
    """파일의 현재 mtime, size 반환."""
    st = path.stat()
    return FileStat(mtime=st.st_mtime, size=st.st_size)

def is_unchanged(current: FileStat, cached: FileStat) -> bool:
    """캐시된 상태와 현재 상태가 같은지."""
    return current.mtime == cached.mtime and current.size == cached.size