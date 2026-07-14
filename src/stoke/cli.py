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
    # Debug: 개발 중 사용, 최적화 없이 디버깅 편함
    build_parser.add_argument(
        "--debug",
        action="store_true",
        help="Debug build (default): -O0 -g, easy to debug",
    )
    # Release: 배포용, 최적화 적용
    build_parser.add_argument(
        "--release",
        action="store_true",
        help="Release build: -O2, optimized for deployment",
    )
    build_parser.add_argument(
        "--profile",
        default=None,
        help="Custom build profile name (defined in stoke.toml)",
    )
    build_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed build output",
    )

    # stoke python list
    python_parser = subparsers.add_parser("python", help="Python version tools")
    python_sub = python_parser.add_subparsers(dest="python_command", required=True)
    python_sub.add_parser("list", help="List installed Python versions")

    # stoke java list
    java_parser = subparsers.add_parser("java", help="Java (JDK) version tools")
    java_sub = java_parser.add_subparsers(dest="java_command", required=True)
    java_sub.add_parser("list", help="List installed JDKs")

    # stoke c list
    c_parser = subparsers.add_parser("c", help="C compiler tools")
    c_sub = c_parser.add_subparsers(dest="c_command", required=True)
    c_sub.add_parser("list", help="List installed C compilers")

    # stoke cpp list
    cpp_parser = subparsers.add_parser("cpp", help="C++ compiler tools")
    cpp_sub = cpp_parser.add_subparsers(dest="cpp_command", required=True)
    cpp_sub.add_parser("list", help="List installed C++ compilers")

    # stoke install <tool> — 도구 자체 설치
    install_parser = subparsers.add_parser("install", help="Install a tool (vcpkg, ...)")
    install_parser.add_argument("tool", choices=["vcpkg"], help="Tool to install")

    # stoke uninstall <tool> — 도구 자체 제거
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a tool (vcpkg, ...)")
    uninstall_parser.add_argument("tool", choices=["vcpkg"], help="Tool to uninstall")

    # stoke vcpkg <subcommand> — vcpkg를 사용해서 라이브러리 관리
    vcpkg_parser = subparsers.add_parser("vcpkg", help="vcpkg library management")
    vcpkg_sub = vcpkg_parser.add_subparsers(dest="vcpkg_command", required=True)

    # 라이브러리 설치
    vcpkg_install_parser = vcpkg_sub.add_parser("install", help="Install a library")
    vcpkg_install_parser.add_argument("library", help="Library name")
    vcpkg_install_parser.add_argument("--version", help="Specific version (default: latest)")
    vcpkg_install_parser.add_argument("--target", help="Target name in stoke.toml")

    # 라이브러리 제거
    vcpkg_remove_parser = vcpkg_sub.add_parser("remove", help="Remove a library")
    vcpkg_remove_parser.add_argument("library", help="Library name")
    vcpkg_remove_parser.add_argument("--target", help="Target name in stoke.toml")

    # 라이브러리 목록
    vcpkg_list_parser = vcpkg_sub.add_parser("list", help="List installed libraries")
    vcpkg_list_parser.add_argument("--target", help="Target name in stoke.toml")

    # vcpkg 버전
    vcpkg_sub.add_parser("version", help="Show installed vcpkg version")
    
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
    run_parser.add_argument(
        "--debug",
        action="store_true",
        help="Run debug build (default, C/C++ only)",
    )
    run_parser.add_argument(
        "--release",
        action="store_true",
        help="Run release build (C/C++ only)",
    )
    run_parser.add_argument(
        "--profile",
        default=None,
        help="Run specific custom profile build (C/C++ only)",
    )

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
        # 프로파일 결정
        if args.debug and args.release:
            print("Error: cannot use both --debug and --release", file=sys.stderr)
            sys.exit(1)
        if(args.debug or args.release) and args.profile:
            flag_name = "--debug" if args.debug else "--release" 
            print(f"Error: cannot use {flag_name} with --release", file=sys.stderr)
            sys.exit(1)

        if args.release:
            profile_name = "release" 
        elif args.profile:
            profile_name = args.profile
        else:
            profile_name = "debug"
        
        cmd_build(args.target, force=args.force, profile=profile_name, verbose=args.verbose)
    elif args.command == "clean":
        cmd_clean(target_name=args.target, delete_lock=args.all)
    elif args.command == "python":
        if args.python_command == "list":
            cmd_python_list()
    elif args.command == "java":
        if args.java_command == "list":
            cmd_java_list()
    elif args.command == "c":
        if args.c_command == "list":
            cmd_c_list()
    elif args.command == "cpp":
        if args.cpp_command == "list":
            cmd_cpp_list()
    elif args.command == "install":
        if args.tool == "vcpkg":
            cmd_install_vcpkg()
    elif args.command == "uninstall":
        if args.tool == "vcpkg":
            cmd_uninstall_vcpkg()
    elif args.command == "vcpkg":
        if args.vcpkg_command == "install":
            cmd_vcpkg_install_library(args.library, args.version, args.target)
        elif args.vcpkg_command == "remove":
            cmd_vcpkg_remove_library(args.library, args.target)
        elif args.vcpkg_command == "list":
            cmd_vcpkg_list_libraries(args.target)
        elif args.vcpkg_command == "version":
            cmd_vcpkg_version()
    elif args.command == "init":
        cmd_init()
    elif args.command == "watch":
        cmd_watch(args.target)
    elif args.command == "hot-reload":
        cmd_hot_reload(args.target)
    elif args.command == "run":
        # 프로파일 결정
        if args.debug and args.release:
            print("Error: cannot use both --debug and --release", file=sys.stderr)
            sys.exit(1)
        if (args.debug or args.release) and args.profile:
            flag_name = "--debug" if args.debug else "--release"
            print(f"Error: cannot use {flag_name} with --profile", file=sys.stderr)
            sys.exit(1)

        if args.release:
            profile_name = "release"
        elif args.profile:
            profile_name = args.profile
        else:
            profile_name = "debug"

        cmd_run(args.target, profile=profile_name)
    elif args.command == "ide-sync":
        cmd_ide_sync()

def cmd_build(target_name, force: bool = False, profile: str = "debug", verbose: bool = False):
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    # 프로파일 유효성 확인
    if profile not in config.profiles:
        print(f"Error: profile '{profile}' not found", file=sys.stderr)
        print(f"Available profiles: {', '.join(config.profiles.keys())}", file=sys.stderr)
        sys.exit(1)
    if target_name is None:
        target_name = next(iter(config.targets))
        if verbose:
            print(f"No target specified, using default: {target_name}")
    if target_name not in config.targets:
        print(f"Error: target '{target_name}' not found in stoke.toml", file=sys.stderr)
        print(f"Available targets: {', '.join(config.targets.keys())}", file=sys.stderr)
        sys.exit(1)
    target = config.targets[target_name]
    print(f"Building '{target.name}' ({target.language})...")
    project_root = config.config_path.parent

    try:
        profile_obj = config.profiles[profile]
        adapter = make_adapter(target, config.project, project_root, profile=profile_obj, verbose=verbose)
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

def cmd_c_list():
    from stoke.c_versions import detect_all as detect_c

    installs = [i for i in detect_c() if i.kind == "c"]
    if not installs:
        print("No C compiler detected.")
        print("Install gcc or ensure it's in your PATH.")
        return

    print(f"Detected {len(installs)} C compiler(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        print(f"  gcc {install.version} (major: {install.major_version}){default_mark}")
        print(f"    executable: {install.executable}")
        print()


def cmd_cpp_list():
    from stoke.c_versions import detect_all as detect_c

    installs = [i for i in detect_c() if i.kind == "cpp"]
    if not installs:
        print("No C++ compiler detected.")
        print("Install g++ or ensure it's in your PATH.")
        return

    print(f"Detected {len(installs)} C++ compiler(s):\n")
    for install in installs:
        default_mark = " (default)" if install.is_default else ""
        print(f"  g++ {install.version} (major: {install.major_version}){default_mark}")
        print(f"    executable: {install.executable}")
        print()

def cmd_install_vcpkg():
    from stoke.vcpkg import install_vcpkg

    try:
        install_vcpkg()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_uninstall_vcpkg():
    from stoke.vcpkg import uninstall_vcpkg

    try:
        uninstall_vcpkg()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_vcpkg_version():
    from stoke.vcpkg import is_vcpkg_installed, get_vcpkg_root, get_vcpkg_version

    if not is_vcpkg_installed():
        print("vcpkg is not installed.")
        print("Run 'stoke vcpkg install' to install it.")
        return

    version = get_vcpkg_version()
    root = get_vcpkg_root()

    if version:
        print(f"vcpkg version: {version}")
    else:
        print(f"vcpkg is installed but version couldn't be determined.")
    print(f"Location: {root}")

def cmd_vcpkg_install_library(library: str, version: str | None, target: str | None):
    """
    stoke vcpkg install <library> [--version=X] [--target=Y]
    """
    from stoke.vcpkg import install_library
    from stoke.c_libraries import can_use_in_c_project
    from stoke.toml_editor import add_dep

    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 타겟 결정
    if target is None:
        target = next(iter(config.targets))
        print(f"No target specified, using: {target}")

    if target not in config.targets:
        print(f"Error: target '{target}' not found in stoke.toml", file=sys.stderr)
        print(f"Available targets: {', '.join(config.targets.keys())}", file=sys.stderr)
        sys.exit(1)

    target_config = config.targets[target]

    # C/C++ 프로젝트인지 확인
    if target_config.language not in ("c", "cpp"):
        print(
            f"Error: vcpkg is only for C/C++ projects.\n"
            f"  Target '{target}' is a {target_config.language} project.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 언어 호환성 검증
    if target_config.language == "c":
        if not can_use_in_c_project(library):
            print(
                f"Error: '{library}' is not a C library.\n"
                f"  C project '{target}' cannot use it.\n"
                f"  Consider using a C++ project or a C alternative.",
                file=sys.stderr,
            )
            sys.exit(1)

    # 라이브러리 설치
    try:
        install_library(library, version)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # stoke.toml 업데이트
    stoke_toml_path = config.config_path
    version_str = version if version else "latest"

    try:
        add_dep(stoke_toml_path, target, library, version_str)
        print(f"\nAdded to stoke.toml: {library} = \"{version_str}\"")
    except (OSError, ValueError) as e:
        print(f"Warning: library installed but failed to update stoke.toml: {e}", file=sys.stderr)

def cmd_vcpkg_remove_library(library: str, target: str | None):
    """
    stoke vcpkg remove <library> [--target=Y]
    """
    from stoke.vcpkg import remove_library
    from stoke.toml_editor import remove_dep

    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 타겟 결정
    if target is None:
        target = next(iter(config.targets))
        print(f"No target specified, using: {target}")

    if target not in config.targets:
        print(f"Error: target '{target}' not found in stoke.toml", file=sys.stderr)
        sys.exit(1)

    target_config = config.targets[target]

    if target_config.language not in ("c", "cpp"):
        print(
            f"Error: vcpkg is only for C/C++ projects.\n"
            f"  Target '{target}' is a {target_config.language} project.",
            file=sys.stderr,
        )
        sys.exit(1)

    # stoke.toml에서 제거
    stoke_toml_path = config.config_path
    try:
        removed = remove_dep(stoke_toml_path, target, library)
        if not removed:
            print(f"Warning: '{library}' not found in stoke.toml deps")
    except (OSError, ValueError) as e:
        print(f"Error updating stoke.toml: {e}", file=sys.stderr)
        sys.exit(1)

    # vcpkg에서 제거
    try:
        remove_library(library)
    except RuntimeError as e:
        print(f"Warning: vcpkg remove failed: {e}", file=sys.stderr)

    print(f"\nRemoved from stoke.toml: {library}")


def cmd_vcpkg_list_libraries(target: str | None):
    """
    stoke vcpkg list [--target=Y]
    """
    from stoke.toml_editor import list_deps

    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 타겟 결정
    if target is None:
        target = next(iter(config.targets))

    if target not in config.targets:
        print(f"Error: target '{target}' not found in stoke.toml", file=sys.stderr)
        sys.exit(1)

    target_config = config.targets[target]

    if target_config.language not in ("c", "cpp"):
        print(
            f"Error: vcpkg is only for C/C++ projects.\n"
            f"  Target '{target}' is a {target_config.language} project.",
            file=sys.stderr,
        )
        sys.exit(1)

    stoke_toml_path = config.config_path
    deps = list_deps(stoke_toml_path, target)

    if not deps:
        print(f"No libraries in target '{target}'")
        return

    print(f"Libraries in target '{target}':")
    for name, version in sorted(deps.items()):
        print(f"  {name} = \"{version}\"")

def cmd_run(target_name, profile: str = "debug"):
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # 프로파일 유효성 확인
    if profile not in config.profiles:
        print(f"Error: profile '{profile}' not found", file=sys.stderr)
        print(f"Available profiles: {', '.join(config.profiles.keys())}", file=sys.stderr)
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
        profile_obj = config.profiles[profile]
        adapter = make_adapter(target, config.project, project_root, profile=profile_obj)
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
        # 기존 workspace 파일이 있으면 삭제
        workspace_name = root.name
        workspace_path = root / f"{workspace_name}.code-workspace"
        if workspace_path.exists():
            workspace_path.unlink()
            print(f"Removed: {workspace_path}")
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

    # 워크스페이스 설정 생성 (자바/파이썬)
    settings = make_workspace_settings(projects_by_language)
    if settings:
        settings_path = write_project_settings(root, settings)
        print(f"\nGenerated: {settings_path}")

    # multi-root workspace 파일 생성 (VSCode가 각 하위 폴더의 .vscode/를 인식하도록)
    from stoke.ide.vscode import make_workspace_file, write_workspace_file

    workspace_content = make_workspace_file(projects, root)
    workspace_path = write_workspace_file(root, workspace_content)
    print(f"Generated: {workspace_path}")
    print(f"\nOpen in VSCode: {workspace_path}")

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