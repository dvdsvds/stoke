import argparse
import sys
from pathlib import Path

from stoke.adapters import make_adapter
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

    # stoke java list
    java_parser = subparsers.add_parser("java", help="Java (JDK) version tools")
    java_sub = java_parser.add_subparsers(dest="java_command", required=True)
    java_sub.add_parser("list", help="List installed JDKs")

    #stoke c/c++ list

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

    # stoke init
    subparsers.add_parser("init", help="Initialize a new stoke project")

    # stoke watch [target]
    watch_parser = subparsers.add_parser(
        "watch",
        help="Watch for file changes and rebuild automatically",
    )
    watch_parser.add_argument("target", nargs="?", help="Target name")

    # stoke run [target]
    run_parser = subparsers.add_parser(
        "run",
        help="Run the built target (Python: entry file, Java: main_class)",
    )
    run_parser.add_argument("target", nargs="?", help="Target name")

    subparsers.add_parser(
        "ide-sync",
        help="Scan for stoke projects and generate workspace .vscode/settings.json",
    )

    # stoke hot-reload [target]
    hotreload_parser = subparsers.add_parser(
        "hot-reload",
        help="Watch, rebuild, and restart the running process on changes",
    )
    hotreload_parser.add_argument("target", nargs="?", help="Target name")

    args = parser.parse_args()

    if args.command == "build":
        cmd_build(args.target, force=args.force)
    elif args.command == "clean":
        cmd_clean(target_name=args.target, delete_lock=args.all)
    elif args.command == "python":
        if args.python_command == "list":
            cmd_python_list()
    elif args.command == "java":
        if args.java_command == "list":
            cmd_java_list()
    elif args.command == "init":
        cmd_init()
    elif args.command == "watch":
        cmd_watch(args.target)
    elif args.command == "hot-reload":
        cmd_hot_reload(args.target)
    elif args.command == "run":
        cmd_run(args.target)
    elif args.command == "ide-sync":
        cmd_ide_sync()

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

    try:
        adapter = make_adapter(target, config.project, project_root)
        adapter.build(force=force)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
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

    # 1.5. .stoke/python, .stoke/java 등 언어 폴더가 비었으면 삭제
    for lang in ["python", "java", "c", "cpp"]:
        lang_parent = project_root / ".stoke" / lang
        if lang_parent.exists() and not any(lang_parent.iterdir()):
            lang_parent.rmdir()

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

def cmd_java_list():
    from stoke.java_versions import detect_all as detect_java

    installs = detect_java()
    if not installs:
        print("No JDK detected.")
        print("Install a JDK or set the JAVA_HOME environment variable.")
        return

    print(f"Detected {len(installs)} JDK(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        print(f"  Java {install.version} (major: {install.major_version}){default_mark}")
        print(f"    JAVA_HOME: {install.java_home}")
        print(f"    javac:     {install.javac}")
        print(f"    java:      {install.java}")
        print()

def cmd_run(target_name):
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
        print(f"No target specified, running default: {target_name}")

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

    target = config.targets[target_name]
    project_root = config.config_path.parent

    from stoke.adapters import make_adapter

    try:
        adapter = make_adapter(target, config.project, project_root)
        exit_code = adapter.run()
        sys.exit(exit_code)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_ide_sync():
    from stoke.ide.vscode import (
        find_stoke_projects,
        make_workspace_settings,
        write_project_settings,
    )
    import tomllib

    root = Path.cwd()
    print(f"Scanning for stoke projects under {root}...")

    projects = find_stoke_projects(root)
    if not projects:
        print("No stoke projects found.")
        return

    print(f"Found {len(projects)} project(s):")

    # 언어별로 분류
    projects_by_language = {}
    for project_path in projects:
        stoke_toml = project_path / "stoke.toml"
        try:
            with open(stoke_toml, "rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError) as e:
            print(f"  Skipping {project_path.name} (invalid stoke.toml): {e}")
            continue

        targets = data.get("targets", {})
        if not targets:
            print(f"  Skipping {project_path.name} (no targets)")
            continue

        # 첫 번째 타겟의 언어 사용 (여러 타겟 있어도 대표)
        first_target = next(iter(targets.values()))
        language = first_target.get("language")
        if not language:
            print(f"  Skipping {project_path.name} (no language)")
            continue

        # 상대 경로 계산
        try:
            rel_path = project_path.relative_to(root)
        except ValueError:
            rel_path = project_path

        print(f"  [{language}] {rel_path}")

        if language not in projects_by_language:
            projects_by_language[language] = []

        # 파이썬은 dict로 (경로 정보 여러 개 필요)
        if language == "python":
            projects_by_language[language].append({
                "absolute": project_path,
                "relative": rel_path,
            })
        else:
            # 자바 등은 상대 경로만
            projects_by_language[language].append(rel_path)

    # 워크스페이스 설정 생성
    settings = make_workspace_settings(projects_by_language)
    if not settings:
        print("No settings to generate.")
        return

    settings_path = write_project_settings(root, settings)
    print(f"\nGenerated: {settings_path}")

def cmd_watch(target_name):
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
        print(f"No target specified, watching default: {target_name}")

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

    target = config.targets[target_name]
    project_root = config.config_path.parent

    from stoke.watcher import watch

    try:
        watch(target, config, project_root)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_hot_reload(target_name):
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
        print(f"No target specified, hot-reloading default: {target_name}")

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

    target = config.targets[target_name]
    project_root = config.config_path.parent

    from stoke.hot_reload import hot_reload

    try:
        hot_reload(target, config, project_root)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)