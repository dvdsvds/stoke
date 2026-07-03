import argparse
import sys

from stoke.adapters.python import PythonAdapter
from stoke.config import load_config
from stoke.init import cmd_init
from stoke.python_versions import detect_all


def main():
    parser = argparse.ArgumentParser(
        prog="stoke",
        description="A build tool for multiple languages"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="Build a target")
    build_parser.add_argument("target", nargs="?", help="Target name")
    build_parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore cache and rebuild everything",
    )

    # stoke python list
    python_parser = subparsers.add_parser("python", help="Python version tools")
    python_sub = python_parser.add_subparsers(dest="python_command", required=True)
    python_sub.add_parser("list", help="List installed Python versions")

    # stoke init
    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    clean_parser.add_argument(
        "--all",
        action="store_true",
        help="Also delete lock file (full reset)",
    )
    clean_parser.add_argument(
        "target",
        nargs="?",
        help="Target name (default: all targets)",
    )

    args = parser.parse_args()

    if args.command == "build":
        cmd_build(args.target, force=args.force)
    elif args.command == "clean":
        cmd_clean(target_name=args.target, delete_lock=args.all)
    elif args.command == "python":
        if args.python_command == "list":
            cmd_python_list()
    elif args.command == "init":
        cmd_init()


def cmd_build(target_name, force: bool = False):
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if target_name is None:
        target_name = next(iter(config.targets))
        print(f"No target specified, using default: {target_name}")

    if target_name not in config.targets:
        print(f"Error: target '{target_name}' not found in stoke.toml", file=sys.stderr)
        print(f"Available targets: {', '.join(config.targets.keys())}", file=sys.stderr)
        sys.exit(1)

    target = config.targets[target_name]
    print(f"Building target '{target.name}' (language: {target.language})...")

    project_root = config.config_path.parent

    if target.language == "python":
        adapter = PythonAdapter(target, config.project, project_root)
        try:
            adapter.build(force=force)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(
            f"Error: language '{target.language}' not supported yet",
            file=sys.stderr,
        )
        sys.exit(1)


def cmd_clean(target_name: str | None = None, delete_lock: bool = False):
    import shutil
    from stoke.lock import _lock_path

    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

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

    # 1. venv 삭제 (타겟별)
    for name in targets_to_clean:
        venv_dir = project_root / ".stoke" / "venv" / name
        if venv_dir.exists():
            shutil.rmtree(venv_dir)
            print(f"Deleted venv: {venv_dir}")
            deleted_count += 1

    # 1.5. .stoke/venv/ 상위 폴더가 비었으면 삭제
    venv_parent = project_root / ".stoke" / "venv"
    if venv_parent.exists() and not any(venv_parent.iterdir()):
        venv_parent.rmdir()

    # 2. __pycache__ 삭제 (프로젝트 루트 하위 전체, .stoke 제외)
    pycache_count = 0
    for pycache in project_root.rglob("__pycache__"):
        # .stoke 폴더 안의 __pycache__는 위에서 이미 지웠거나 처리됨
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
        # 안에 뭐가 남아있는지 확인
        remaining = list(stoke_dir.rglob("*"))
        if not remaining:
            stoke_dir.rmdir()
            print(f"Removed empty .stoke directory")

    if deleted_count == 0:
        print("Nothing to clean")
    else:
        print(f"\nClean complete: {deleted_count} item(s) removed")


def cmd_python_list():
    installs = detect_all()
    if not installs:
        print("No Python installations detected.")
        return

    print(f"Detected {len(installs)} Python installation(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        print(f"  Python {install.version}{default_mark}")
        print(f"    -> {install.executable}")