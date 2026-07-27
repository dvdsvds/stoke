"""stoke CLI 진입점."""
import argparse
import sys

from stoke.cli.messages import get_message as _

from stoke.cli.utils import resolve_profile_from_args, add_debug_release_profile_args
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
from stoke.cli.install_lang import (
    cmd_install_language,
    cmd_list_language_versions,
    cmd_uninstall_language,
)
from stoke.cli.ide import cmd_ide_sync
from stoke.init import cmd_init

from stoke.languages.python.frameworks.fastapi import cmd_init_fastapi
from stoke.languages.python.frameworks.flask import cmd_init_flask
from stoke.languages.python.frameworks.django import cmd_init_django

from stoke.languages.java.frameworks.spring_boot import cmd_init_spring_boot

from stoke.languages.go.frameworks.gin import cmd_init_gin
from stoke.languages.go.frameworks.echo import cmd_init_echo
from stoke.languages.go.frameworks.fiber import cmd_init_fiber
from stoke.languages.go.frameworks.chi import cmd_init_chi

from stoke.languages.rust.frameworks.actix_web import cmd_init_actix_web
from stoke.languages.rust.frameworks.axum import cmd_init_axum
from stoke.languages.rust.frameworks.rocket import cmd_init_rocket

from stoke.languages.kotlin.frameworks.ktor import cmd_init_ktor
from stoke.languages.kotlin.frameworks.spring_boot import cmd_init_spring_boot_kotlin

from stoke.languages.csharp.frameworks.aspnet_core import cmd_init_aspnet_core

from stoke.languages.ruby.frameworks.sinatra import cmd_init_sinatra

from stoke.languages.php.frameworks.slim import cmd_init_slim

from stoke.languages.javascript.frameworks.express import cmd_init_express
from stoke.languages.javascript.frameworks.fastify import cmd_init_fastify

from stoke.languages.typescript.frameworks.nextjs import cmd_init_nextjs
from stoke.languages.typescript.frameworks.nestjs import cmd_init_nestjs
from stoke.languages.typescript.frameworks.vite import cmd_init_vite
from stoke.languages.typescript.frameworks.nuxt import cmd_init_nuxt
from stoke.languages.typescript.frameworks.sveltekit import cmd_init_sveltekit
from stoke.languages.typescript.frameworks.hono import cmd_init_hono

_INIT_FRAMEWORK_HANDLERS = {
    "spring-boot": cmd_init_spring_boot,
    "fastapi": cmd_init_fastapi,
    "flask": cmd_init_flask,
    "django": cmd_init_django,
    "gin": cmd_init_gin,
    "echo": cmd_init_echo,
    "fiber": cmd_init_fiber,
    "chi": cmd_init_chi,
    "actix-web": cmd_init_actix_web,
    "axum": cmd_init_axum,
    "rocket": cmd_init_rocket,
    "ktor": cmd_init_ktor,
    "spring-boot-kotlin": cmd_init_spring_boot_kotlin,
    "aspnet-core": cmd_init_aspnet_core,
    "sinatra": cmd_init_sinatra,
    "slim": cmd_init_slim,
    "nextjs": cmd_init_nextjs,
    "express": cmd_init_express,
    "nestjs": cmd_init_nestjs,
    "fastify": cmd_init_fastify,
    "vite": cmd_init_vite,
    "nuxt": cmd_init_nuxt,
    "sveltekit": cmd_init_sveltekit,
    "hono": cmd_init_hono,
}

def _build_parser():
    """argparse 파서 구성."""
    parser = argparse.ArgumentParser(
        prog="stoke",
        description=_("prog.description")
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # stoke build
    build_parser = subparsers.add_parser("build", help=_("build.help"))
    build_parser.add_argument("target", nargs="?", help=_("build.target"))
    build_parser.add_argument("--force", action="store_true", help=_("build.force"))
    add_debug_release_profile_args(build_parser, "build")

    # stoke python list
    python_parser = subparsers.add_parser("python", help=_("python.help"))
    python_sub = python_parser.add_subparsers(dest="python_command", required=True)
    python_sub.add_parser("list", help=_("python.list.help"))

    # stoke java list
    java_parser = subparsers.add_parser("java", help=_("java.help"))
    java_sub = java_parser.add_subparsers(dest="java_command", required=True)
    java_sub.add_parser("list", help=_("java.list.help"))

    # stoke c list
    c_parser = subparsers.add_parser("c", help=_("c.help"))
    c_sub = c_parser.add_subparsers(dest="c_command", required=True)
    c_sub.add_parser("list", help=_("c.list.help"))

    # stoke cpp list
    cpp_parser = subparsers.add_parser("cpp", help=_("cpp.help"))
    cpp_sub = cpp_parser.add_subparsers(dest="cpp_command", required=True)
    cpp_sub.add_parser("list", help=_("cpp.list.help"))

    # stoke install <tool> | --language=X --version=Y
    install_parser = subparsers.add_parser("install", help=_("install.help"))
    install_parser.add_argument("tool", nargs="?", choices=["vcpkg"], help=_("install.tool"))
    install_parser.add_argument("--language", help="Language to install (python, java, c, cpp)")
    install_parser.add_argument("--version", default="latest", help="Version (default: latest)")
    install_parser.add_argument("--list", action="store_true", help="List available versions")

    # stoke uninstall <tool> | --language=X --version=Y
    uninstall_parser = subparsers.add_parser("uninstall", help=_("uninstall.help"))
    uninstall_parser.add_argument("tool", nargs="?", choices=["vcpkg"], help=_("uninstall.tool"))
    uninstall_parser.add_argument("--language", help="Language to uninstall (python, java, c, cpp, conda, go)")
    uninstall_parser.add_argument("--version", help="Version to uninstall (optional)")

    # stoke vcpkg <subcommand>
    vcpkg_parser = subparsers.add_parser("vcpkg", help=_("vcpkg.help"))
    vcpkg_sub = vcpkg_parser.add_subparsers(dest="vcpkg_command", required=True)

    vcpkg_install_parser = vcpkg_sub.add_parser("install", help=_("vcpkg.install.help"))
    vcpkg_install_parser.add_argument("library", help=_("vcpkg.install.library"))
    vcpkg_install_parser.add_argument("--version", help=_("vcpkg.install.version"))
    vcpkg_install_parser.add_argument("--target", help=_("vcpkg.install.target"))

    vcpkg_remove_parser = vcpkg_sub.add_parser("remove", help=_("vcpkg.remove.help"))
    vcpkg_remove_parser.add_argument("library", help=_("vcpkg.remove.library"))
    vcpkg_remove_parser.add_argument("--target", help=_("vcpkg.remove.target"))

    vcpkg_list_parser = vcpkg_sub.add_parser("list", help=_("vcpkg.list.help"))
    vcpkg_list_parser.add_argument("--target", help=_("vcpkg.list.target"))

    vcpkg_sub.add_parser("version", help=_("vcpkg.version.help"))

    # stoke clean
    clean_parser = subparsers.add_parser("clean", help=_("clean.help"))
    clean_parser.add_argument("--all", action="store_true", help=_("clean.all"))
    clean_parser.add_argument("target", nargs="?", help=_("clean.target"))

    # stoke init [type]
    init_parser = subparsers.add_parser("init", help=_("init.help"))
    init_parser.add_argument("type", nargs="?", choices=list(_INIT_FRAMEWORK_HANDLERS), help="Project type (optional)")

    # stoke watch
    watch_parser = subparsers.add_parser("watch", help=_("watch.help"))
    watch_parser.add_argument("target", nargs="?", help=_("watch.target"))
    add_debug_release_profile_args(watch_parser, "watch")

    # stoke run
    run_parser = subparsers.add_parser("run", help=_("run.help"))
    run_parser.add_argument("target", nargs="?", help=_("run.target"))
    add_debug_release_profile_args(run_parser, "run", include_verbose=False)

    # stoke ide-sync
    subparsers.add_parser("ide-sync", help=_("ide-sync.help"))

    # stoke hot-reload
    hotreload_parser = subparsers.add_parser("hot-reload", help=_("hot-reload.help"))
    hotreload_parser.add_argument("target", nargs="?", help=_("hot-reload.target"))
    add_debug_release_profile_args(hotreload_parser, "hot-reload")

    return parser

def main():
    parser = _build_parser()
    args = parser.parse_args()

    try:
        _dispatch(args)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)

def _dispatch(args):
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
        if args.language:
            if args.list:
                from stoke.cli.install_lang import cmd_list_language_versions
                cmd_list_language_versions(args.language)
            else:
                cmd_install_language(args.language, args.version)
        elif args.tool == "vcpkg":
            cmd_install_vcpkg()
        else:
            print("Error: specify a tool or --language", file=sys.stderr)
            sys.exit(1)
    elif args.command == "uninstall":
        if args.language:
            cmd_uninstall_language(args.language, args.version)
        elif args.tool == "vcpkg":
            cmd_uninstall_vcpkg()
        else:
            print("Error: specify tool or --language", file=sys.stderr)
            sys.exit(1)
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
        handler = _INIT_FRAMEWORK_HANDLERS.get(args.type)
        if handler:
            handler()
        else:
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