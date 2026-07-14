"""stoke CLI 진입점."""
import argparse
import sys

from stoke.cli.utils import resolve_profile_from_args
from stoke.cli.build import cmd_build, cmd_run, cmd_watch, cmd_hot_reload
from stoke.cli.clean import cmd_clean
from stoke.cli.tools import cmd_python_list, cmd_java_list, cmd_c_list, cmd_cpp_list
from stoke.cli.vcpkg import (
    cmd_install_vcpkg,
    cmd_uninstall_vcpkg,
    cmd_vcpkg_version,
    cmd_vcpkg_install_library,
    cmd_vcpkg_remove_library,
    cmd_vcpkg_list_libraries,
)
from stoke.cli.ide import cmd_ide_sync
from stoke.init import cmd_init


def _build_parser():
    """argparse 파서 구성."""
    parser = argparse.ArgumentParser(
        prog="stoke",
        description="A build tool for multiple languages"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # stoke build
    build_parser = subparsers.add_parser("build", help="Build a target")
    build_parser.add_argument("target", nargs="?", help="Target name")
    build_parser.add_argument("--force", action="store_true", help="Ignore cache and rebuild everything")
    build_parser.add_argument("--debug", action="store_true", help="Debug build (default): -O0 -g, easy to debug")
    build_parser.add_argument("--release", action="store_true", help="Release build: -O2, optimized for deployment")
    build_parser.add_argument("--profile", default=None, help="Custom build profile name (defined in stoke.toml)")
    build_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed build output")

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

    # stoke install <tool>
    install_parser = subparsers.add_parser("install", help="Install a tool (vcpkg, ...)")
    install_parser.add_argument("tool", choices=["vcpkg"], help="Tool to install")

    # stoke uninstall <tool>
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a tool (vcpkg, ...)")
    uninstall_parser.add_argument("tool", choices=["vcpkg"], help="Tool to uninstall")

    # stoke vcpkg <subcommand>
    vcpkg_parser = subparsers.add_parser("vcpkg", help="vcpkg library management")
    vcpkg_sub = vcpkg_parser.add_subparsers(dest="vcpkg_command", required=True)

    vcpkg_install_parser = vcpkg_sub.add_parser("install", help="Install a library")
    vcpkg_install_parser.add_argument("library", help="Library name")
    vcpkg_install_parser.add_argument("--version", help="Specific version (default: latest)")
    vcpkg_install_parser.add_argument("--target", help="Target name in stoke.toml")

    vcpkg_remove_parser = vcpkg_sub.add_parser("remove", help="Remove a library")
    vcpkg_remove_parser.add_argument("library", help="Library name")
    vcpkg_remove_parser.add_argument("--target", help="Target name in stoke.toml")

    vcpkg_list_parser = vcpkg_sub.add_parser("list", help="List installed libraries")
    vcpkg_list_parser.add_argument("--target", help="Target name in stoke.toml")

    vcpkg_sub.add_parser("version", help="Show installed vcpkg version")

    # stoke clean
    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    clean_parser.add_argument("--all", action="store_true", help="Also delete lock file (full reset)")
    clean_parser.add_argument("target", nargs="?", help="Target name (default: all targets)")

    # stoke init
    subparsers.add_parser("init", help="Initialize a new stoke project")

    # stoke watch
    watch_parser = subparsers.add_parser("watch", help="Watch for file changes and rebuild automatically")
    watch_parser.add_argument("target", nargs="?", help="Target name")
    watch_parser.add_argument("--debug", action="store_true", help="Debug build (default, C/C++ only)")
    watch_parser.add_argument("--release", action="store_true", help="Release build (C/C++ only)")
    watch_parser.add_argument("--profile", default=None, help="Custom build profile name (C/C++ only)")
    watch_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed build output")

    # stoke run
    run_parser = subparsers.add_parser("run", help="Run the built target (Python: entry file, Java: main_class)")
    run_parser.add_argument("target", nargs="?", help="Target name")
    run_parser.add_argument("--debug", action="store_true", help="Run debug build (default, C/C++ only)")
    run_parser.add_argument("--release", action="store_true", help="Run release build (C/C++ only)")
    run_parser.add_argument("--profile", default=None, help="Run specific custom profile build (C/C++ only)")

    # stoke ide-sync
    subparsers.add_parser("ide-sync", help="Scan for stoke projects and generate workspace .vscode/settings.json")

    # stoke hot-reload
    hotreload_parser = subparsers.add_parser("hot-reload", help="Watch, rebuild, and restart the running process on changes")
    hotreload_parser.add_argument("target", nargs="?", help="Target name")
    hotreload_parser.add_argument("--debug", action="store_true", help="Debug build (default, C/C++ only)")
    hotreload_parser.add_argument("--release", action="store_true", help="Release build (C/C++ only)")
    hotreload_parser.add_argument("--profile", default=None, help="Custom build profile name (C/C++ only)")
    hotreload_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed build output")

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "build":
        profile_name = resolve_profile_from_args(args)
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
        profile_name = resolve_profile_from_args(args)
        cmd_watch(args.target, profile=profile_name, verbose=args.verbose)
    elif args.command == "hot-reload":
        profile_name = resolve_profile_from_args(args)
        cmd_hot_reload(args.target, profile=profile_name, verbose=args.verbose)
    elif args.command == "run":
        profile_name = resolve_profile_from_args(args)
        cmd_run(args.target, profile=profile_name)
    elif args.command == "ide-sync":
        cmd_ide_sync()