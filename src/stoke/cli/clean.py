"""clean 명령어."""
import sys
import shutil
from stoke.lock import _lock_path
from stoke.cli.utils import load_config_or_exit


def cmd_clean(target_name: str | None = None, delete_lock: bool = False):
    config = load_config_or_exit()
    project_root = config.config_path.parent

    # 타겟 지정됐으면 그것만, 아니면 전체
    if target_name is not None:
        if target_name not in config.targets:
            print(
                f"Error: target '{target_name}' not found in stoke.toml",
                file=sys.stderr,
            )
            print(
                f"Available targets: {', '.join(config.targets.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)
        targets_to_clean = [target_name]
    else:
        targets_to_clean = list(config.targets.keys())

    deleted_count = 0

    # 1. 언어별 타겟 폴더 삭제
    for name in targets_to_clean:
        target = config.targets.get(name)
        if target is None:
            continue

        if target.language == "python":
            lang_target_dir = project_root / ".stoke" / "python" / name
            if lang_target_dir.exists():
                shutil.rmtree(lang_target_dir)
                print(f"Deleted Python target dir: {lang_target_dir}")
                deleted_count += 1
        elif target.language == "java":
            lang_target_dir = project_root / ".stoke" / "java" / name
            if lang_target_dir.exists():
                shutil.rmtree(lang_target_dir)
                print(f"Deleted Java target dir: {lang_target_dir}")
                deleted_count += 1
        elif target.language == "c":
            lang_target_dir = project_root / ".stoke" / "c" / name
            if lang_target_dir.exists():
                shutil.rmtree(lang_target_dir)
                print(f"Deleted C target dir: {lang_target_dir}")
                deleted_count += 1
        elif target.language == "cpp":
            lang_target_dir = project_root / ".stoke" / "cpp" / name
            if lang_target_dir.exists():
                shutil.rmtree(lang_target_dir)
                print(f"Deleted C++ target dir: {lang_target_dir}")
                deleted_count += 1

    # 1.5. .stoke/python, .stoke/java 등 언어 폴더가 비었으면 삭제
    for lang in ["python", "java", "c", "cpp"]:
        lang_parent = project_root / ".stoke" / lang
        if lang_parent.exists() and not any(lang_parent.iterdir()):
            lang_parent.rmdir()

    # 2. __pycache__ 삭제 (프로젝트 루트 하위 전체, .stoke 제외)
    pycache_count = 0
    for pycache in project_root.rglob("__pycache__"):
        try:
            pycache.relative_to(project_root / ".stoke")
            continue
        except ValueError:
            pass

        if pycache.is_dir():
            shutil.rmtree(pycache)
            pycache_count += 1

    if pycache_count > 0:
        print(f"Deleted {pycache_count} __pycache__ folder(s)")
        deleted_count += pycache_count

    # 2.5. cache.json 삭제 (타겟 지정 안 됐을 때만)
    if target_name is None:
        cache_file = project_root / ".stoke" / "cache.json"
        if cache_file.exists():
            cache_file.unlink()
            print(f"Deleted cache: {cache_file}")
            deleted_count += 1

    # 3. lock 파일 삭제 (--all 옵션인 경우만)
    if delete_lock:
        lock_path = _lock_path(project_root, config.project.lock_mode)
        if lock_path.exists():
            lock_path.unlink()
            print(f"Deleted lock file: {lock_path}")
            deleted_count += 1

    # 4. .stoke 폴더 자체가 비었으면 삭제
    stoke_dir = project_root / ".stoke"
    if stoke_dir.exists():
        remaining = list(stoke_dir.rglob("*"))
        if not remaining:
            stoke_dir.rmdir()
            print(f"Removed empty .stoke directory")

    if deleted_count == 0:
        print("Nothing to clean")
    else:
        print(f"\nClean complete: {deleted_count} item(s) removed")