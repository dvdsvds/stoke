"""stoke CLI 진입점."""
import argparse
import os
import re
import shutil
import sys
from pathlib import Path

from stoke import __version__
from stoke.cli.messages import get_message as _

from stoke.cli.utils import resolve_profile_from_args, add_debug_release_profile_args, load_config_or_exit
from stoke.cli.build import cmd_build, cmd_run, cmd_watch, cmd_hot_reload, cmd_test
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
    SUPPORTED_LANGUAGES,
)
from stoke.cli.ide import cmd_ide_sync
from stoke.cli.deps import cmd_add_dep, cmd_remove_dep
from stoke.cli.exec_cmd import cmd_exec
from stoke.cli.audit import cmd_audit
from stoke.cli.outdated import cmd_outdated
from stoke.cli.sbom import cmd_sbom
from stoke.cli.doctor import cmd_doctor
from stoke.cli.self_update import cmd_self_update
from stoke.cli.completions import cmd_completions, cmd_complete_targets
from stoke.cli.git_cmd import cmd_git
from stoke.cli.new_cmd import cmd_new
from stoke.cli.workspace import run_across_workspace
from stoke.init import cmd_init, cmd_init_noninteractive, cmd_init_workspace

from stoke.languages.python.frameworks.fastapi import cmd_init_fastapi
from stoke.languages.python.frameworks.flask import cmd_init_flask
from stoke.languages.python.frameworks.django import cmd_init_django

from stoke.languages.java.frameworks.spring_boot import cmd_init_spring_boot

from stoke.languages.go.frameworks.gin import cmd_init_gin
from stoke.languages.go.frameworks.echo import cmd_init_echo
from stoke.languages.go.frameworks.fiber import cmd_init_fiber
from stoke.languages.go.frameworks.chi import cmd_init_chi
from stoke.languages.go.frameworks.bubbletea import cmd_init_bubbletea

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
    "bubbletea": cmd_init_bubbletea,
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

def _help_formatter(prog):
    """기본 HelpFormatter보다 넓게(터미널 폭까지) + 설명 칸을 더 띄움."""
    width = min(shutil.get_terminal_size(fallback=(100, 24)).columns - 2, 100)
    return argparse.HelpFormatter(prog, max_help_position=32, width=width)

_INVALID_CHOICE_RE = re.compile(
    r"^argument ([^:]+): invalid choice: '([^']+)' \(choose from (.+)\)$"
)

class _StokeArgumentParser(argparse.ArgumentParser):
    """invalid-choice 에러를 한 줄 콤마 나열 대신 후보를 한 줄에 하나씩 보여주도록 재포맷."""

    def error(self, message):
        match = _INVALID_CHOICE_RE.match(message)
        if match:
            arg, choice, options = match.groups()
            option_list = [o.strip().strip("'\"") for o in options.split(",")]
            self.print_usage(sys.stderr)
            print(f"{self.prog}: error: '{choice}' isn't a valid {arg}. Choose from:", file=sys.stderr)
            for opt in option_list:
                print(f"  {opt}", file=sys.stderr)
            self.exit(2)
        super().error(message)

def _build_parser():
    """argparse 파서 구성."""
    parser = _StokeArgumentParser(
        prog="stoke",
        description=_("prog.description"),
        formatter_class=_help_formatter,
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"stoke {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="<command>", parser_class=_StokeArgumentParser)

    # stoke build
    build_parser = subparsers.add_parser("build", help=_("build.help"), formatter_class=_help_formatter)
    build_parser.add_argument("target", nargs="?", help=_("build.target"))
    build_parser.add_argument("--force", action="store_true", help=_("build.force"))
    build_parser.add_argument("--all", action="store_true", help=_("build.all"))
    add_debug_release_profile_args(build_parser, "build")

    # stoke python list
    python_parser = subparsers.add_parser("python", help=_("python.help"), formatter_class=_help_formatter)
    python_sub = python_parser.add_subparsers(dest="python_command", required=True)
    python_sub.add_parser("list", help=_("python.list.help"), formatter_class=_help_formatter)

    # stoke java list
    java_parser = subparsers.add_parser("java", help=_("java.help"), formatter_class=_help_formatter)
    java_sub = java_parser.add_subparsers(dest="java_command", required=True)
    java_sub.add_parser("list", help=_("java.list.help"), formatter_class=_help_formatter)

    # stoke c list
    c_parser = subparsers.add_parser("c", help=_("c.help"), formatter_class=_help_formatter)
    c_sub = c_parser.add_subparsers(dest="c_command", required=True)
    c_sub.add_parser("list", help=_("c.list.help"), formatter_class=_help_formatter)

    # stoke cpp list
    cpp_parser = subparsers.add_parser("cpp", help=_("cpp.help"), formatter_class=_help_formatter)
    cpp_sub = cpp_parser.add_subparsers(dest="cpp_command", required=True)
    cpp_sub.add_parser("list", help=_("cpp.list.help"), formatter_class=_help_formatter)

    # stoke install <vcpkg|language> | --language=X --version=Y (--language kept for backwards compatibility)
    install_parser = subparsers.add_parser("install", help=_("install.help"), formatter_class=_help_formatter)
    install_parser.add_argument("tool", nargs="?", choices=["vcpkg"] + list(SUPPORTED_LANGUAGES), metavar="<tool>", help=_("install.tool"))
    install_parser.add_argument("--language", help="Language to install (deprecated, use the positional argument instead, e.g. 'stoke install python')")
    install_parser.add_argument("--version", default="latest", help="Version (default: latest)")
    install_parser.add_argument("--list", action="store_true", help="List available versions")
    install_parser.add_argument("--base-url", help="Override the version metadata base URL (default: STOKE_VERSION_API_BASE env var, or stoke's own endpoint). For mirroring on a locked-down network.")

    # stoke uninstall <vcpkg|language> | --language=X --version=Y (--language kept for backwards compatibility)
    uninstall_parser = subparsers.add_parser("uninstall", help=_("uninstall.help"), formatter_class=_help_formatter)
    uninstall_parser.add_argument("tool", nargs="?", choices=["vcpkg"] + list(SUPPORTED_LANGUAGES), metavar="<tool>", help=_("uninstall.tool"))
    uninstall_parser.add_argument("--language", help="Language to uninstall (deprecated, use the positional argument instead, e.g. 'stoke uninstall python')")
    uninstall_parser.add_argument("--version", help="Version to uninstall (optional)")

    # stoke vcpkg <subcommand>
    vcpkg_parser = subparsers.add_parser("vcpkg", help=_("vcpkg.help"), formatter_class=_help_formatter)
    vcpkg_sub = vcpkg_parser.add_subparsers(dest="vcpkg_command", required=True, metavar="<command>")

    vcpkg_install_parser = vcpkg_sub.add_parser("install", help=_("vcpkg.install.help"), formatter_class=_help_formatter)
    vcpkg_install_parser.add_argument("library", help=_("vcpkg.install.library"))
    vcpkg_install_parser.add_argument("--version", help=_("vcpkg.install.version"))
    vcpkg_install_parser.add_argument("--target", help=_("vcpkg.install.target"))

    vcpkg_remove_parser = vcpkg_sub.add_parser("remove", help=_("vcpkg.remove.help"), formatter_class=_help_formatter)
    vcpkg_remove_parser.add_argument("library", help=_("vcpkg.remove.library"))
    vcpkg_remove_parser.add_argument("--target", help=_("vcpkg.remove.target"))

    vcpkg_list_parser = vcpkg_sub.add_parser("list", help=_("vcpkg.list.help"), formatter_class=_help_formatter)
    vcpkg_list_parser.add_argument("--target", help=_("vcpkg.list.target"))

    vcpkg_sub.add_parser("version", help=_("vcpkg.version.help"), formatter_class=_help_formatter)

    # stoke clean
    clean_parser = subparsers.add_parser("clean", help=_("clean.help"), formatter_class=_help_formatter)
    clean_parser.add_argument("--all", action="store_true", help=_("clean.all"))
    clean_parser.add_argument("target", nargs="?", help=_("clean.target"))

    # stoke init [type]
    init_parser = subparsers.add_parser("init", help=_("init.help"), formatter_class=_help_formatter)
    from stoke.plugins import all_framework_plugin_names
    init_parser.add_argument("type", nargs="?", choices=list(_INIT_FRAMEWORK_HANDLERS) + all_framework_plugin_names(), metavar="<type>", help="Project type (optional, e.g. fastapi, express, spring-boot -- run with no type for an interactive picker)")
    init_parser.add_argument("path", nargs="?", help="Directory to create the project in (created if it doesn't exist; defaults to current directory)")
    init_parser.add_argument("-l", "--language", help="Language (non-interactive mode, e.g. -l python)")
    init_parser.add_argument("--name", help="Project name (non-interactive mode; defaults to current folder name)")
    init_parser.add_argument("-V", "--version", help="Language version/standard/toolchain pin (non-interactive mode; meaning depends on language)")
    init_parser.add_argument("--env-type", choices=["venv", "conda"], help="Python environment type (non-interactive mode; default venv)")
    init_parser.add_argument("--lock-mode", choices=["commit", "local"], default="commit", help="Lock file mode (non-interactive mode; default commit)")
    init_parser.add_argument("--vcpkg", action="store_true", help="Install vcpkg for C/C++ if not already installed (non-interactive mode)")
    init_parser.add_argument("--yes", action="store_true", help="Overwrite an existing stoke.toml without prompting (non-interactive mode)")
    init_parser.add_argument("-w", "--workspace", action="store_true", help="Create a workspace root instead of a single project -- no language/target, just a members list for 'stoke new' to add services to")

    # stoke new <name> -l <language> [-V <version>]  (monorepo: add a service as its own subdirectory)
    new_parser = subparsers.add_parser("new", help=_("new.help"), formatter_class=_help_formatter)
    new_parser.add_argument("name", help=_("new.name"))
    new_parser.add_argument("-l", "--language", help=_("new.language"))
    new_parser.add_argument("-V", "--version", help=_("new.version"))
    new_parser.add_argument("--env-type", choices=["venv", "conda"], help=_("new.env_type"))
    new_parser.add_argument("--lock-mode", choices=["commit", "local"], default="commit", help=_("new.lock_mode"))
    new_parser.add_argument("--vcpkg", action="store_true", help=_("new.vcpkg"))

    # stoke watch
    watch_parser = subparsers.add_parser("watch", help=_("watch.help"), formatter_class=_help_formatter)
    watch_parser.add_argument("target", nargs="?", help=_("watch.target"))
    add_debug_release_profile_args(watch_parser, "watch")

    # stoke run
    run_parser = subparsers.add_parser("run", help=_("run.help"), formatter_class=_help_formatter)
    run_parser.add_argument("target", nargs="?", help=_("run.target"))
    run_parser.add_argument("entry_file", nargs="?", help=_("run.entry_file"))
    add_debug_release_profile_args(run_parser, "run", include_verbose=False)

    # stoke test
    test_parser = subparsers.add_parser("test", help=_("test.help"), formatter_class=_help_formatter)
    test_parser.add_argument("target", nargs="?", help=_("test.target"))
    test_parser.add_argument("--all", action="store_true", help=_("test.all"))
    add_debug_release_profile_args(test_parser, "test")

    # stoke add / remove (python/java dependency management)
    add_parser = subparsers.add_parser("add", help=_("add.help"), formatter_class=_help_formatter)
    add_parser.add_argument("packages", nargs="+", help=_("add.package"))
    add_parser.add_argument("--target", help=_("add.target"))

    remove_parser = subparsers.add_parser("remove", help=_("remove.help"), formatter_class=_help_formatter)
    remove_parser.add_argument("packages", nargs="+", help=_("remove.package"))
    remove_parser.add_argument("--target", help=_("remove.target"))

    # stoke exec [--target=X] -- <command...>
    exec_parser = subparsers.add_parser("exec", help=_("exec.help"), formatter_class=_help_formatter)
    exec_parser.add_argument("--target", help=_("exec.target"))
    exec_parser.add_argument("command_args", nargs=argparse.REMAINDER, help=_("exec.command"), metavar="command")

    # stoke audit [--target=X]
    audit_parser = subparsers.add_parser("audit", help=_("audit.help"), formatter_class=_help_formatter)
    audit_parser.add_argument("--target", help=_("audit.target"))
    audit_parser.add_argument("--json", action="store_true", help=_("audit.json"))

    # stoke outdated [--target=X]
    outdated_parser = subparsers.add_parser("outdated", help=_("outdated.help"), formatter_class=_help_formatter)
    outdated_parser.add_argument("--target", help=_("outdated.target"))
    outdated_parser.add_argument("--json", action="store_true", help=_("outdated.json"))

    # stoke sbom [--target=X] [--format] [--output]
    sbom_parser = subparsers.add_parser("sbom", help=_("sbom.help"), formatter_class=_help_formatter)
    sbom_parser.add_argument("--target", help=_("sbom.target"))
    sbom_parser.add_argument("--format", choices=["cyclonedx", "spdx"], default="cyclonedx", help=_("sbom.format"))
    sbom_parser.add_argument("--output", help=_("sbom.output"))

    # stoke doctor [--target=X]
    doctor_parser = subparsers.add_parser("doctor", help=_("doctor.help"), formatter_class=_help_formatter)
    doctor_parser.add_argument("--target", help=_("doctor.target"))
    doctor_parser.add_argument("--json", action="store_true", help=_("doctor.json"))

    # stoke self-update [--check] [--yes]
    self_update_parser = subparsers.add_parser("self-update", help=_("self-update.help"), formatter_class=_help_formatter)
    self_update_parser.add_argument("--check", action="store_true", help=_("self-update.check"))
    self_update_parser.add_argument("--yes", action="store_true", help=_("self-update.yes"))

    # stoke completions <bash|zsh|fish>
    completions_parser = subparsers.add_parser("completions", help=_("completions.help"), formatter_class=_help_formatter)
    completions_parser.add_argument("shell", choices=["bash", "zsh", "fish"], help=_("completions.shell"))

    # stoke complete-targets -- hidden, used by the generated shell completion scripts.
    # help=SUPPRESS doesn't actually drop the row from the subcommand listing, so remove
    # its pseudo-action from the listing directly (it stays reachable via .choices for parsing).
    subparsers.add_parser("complete-targets")
    subparsers._choices_actions = [a for a in subparsers._choices_actions if a.dest != "complete-targets"]

    # stoke git -- interactive add/commit/push menu
    subparsers.add_parser("git", help=_("git.help"), formatter_class=_help_formatter)

    # stoke ide-sync
    subparsers.add_parser("ide-sync", help=_("ide-sync.help"), formatter_class=_help_formatter)

    # stoke hot-reload
    hotreload_parser = subparsers.add_parser("hot-reload", help=_("hot-reload.help"), formatter_class=_help_formatter)
    hotreload_parser.add_argument("target", nargs="?", help=_("hot-reload.target"))
    add_debug_release_profile_args(hotreload_parser, "hot-reload")

    return parser

def main():
    parser = _build_parser()

    if sys.argv[1:2] == ["help"]:
        parser.parse_args(sys.argv[2:3] + ["--help"] if sys.argv[2:3] else ["--help"])
        return

    args = parser.parse_args()

    try:
        _dispatch(args)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)

def _dispatch(args):
    if args.command == "build":
        profile_name = resolve_profile_from_args(args)
        if args.all:
            config = load_config_or_exit()
            run_across_workspace(config, lambda: cmd_build(None, force=args.force, profile=profile_name, verbose=args.verbose))
        else:
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
        language = args.language or (args.tool if args.tool != "vcpkg" else None)
        if language:
            if args.list:
                from stoke.cli.install_lang import cmd_list_language_versions
                cmd_list_language_versions(language, base_url=args.base_url)
            else:
                cmd_install_language(language, args.version, base_url=args.base_url)
        elif args.tool == "vcpkg":
            cmd_install_vcpkg()
        else:
            print(f"Error: specify a language ({', '.join(SUPPORTED_LANGUAGES)}) or 'vcpkg', e.g. 'stoke install python'", file=sys.stderr)
            sys.exit(1)
    elif args.command == "uninstall":
        language = args.language or (args.tool if args.tool != "vcpkg" else None)
        if language:
            cmd_uninstall_language(language, args.version)
        elif args.tool == "vcpkg":
            cmd_uninstall_vcpkg()
        else:
            print(f"Error: specify a language ({', '.join(SUPPORTED_LANGUAGES)}) or 'vcpkg', e.g. 'stoke uninstall python'", file=sys.stderr)
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
        from stoke.plugins import get_framework_plugin
        if args.path:
            target_dir = Path(args.path)
            target_dir.mkdir(parents=True, exist_ok=True)
            os.chdir(target_dir)
        handler = _INIT_FRAMEWORK_HANDLERS.get(args.type) or get_framework_plugin(args.type)
        if args.workspace:
            cmd_init_workspace(project_name=args.name, yes=args.yes)
        elif handler:
            handler()
        elif args.language:
            cmd_init_noninteractive(
                language=args.language,
                project_name=args.name,
                version=args.version,
                env_type=args.env_type,
                lock_mode=args.lock_mode,
                vcpkg=args.vcpkg,
                yes=args.yes,
            )
        else:
            cmd_init()
    elif args.command == "new":
        cmd_new(
            name=args.name,
            language=args.language,
            version=args.version,
            env_type=args.env_type,
            lock_mode=args.lock_mode,
            vcpkg=args.vcpkg,
        )
    elif args.command == "watch":
        profile_name = resolve_profile_from_args(args)
        cmd_watch(args.target, profile=profile_name, verbose=args.verbose)
    elif args.command == "hot-reload":
        profile_name = resolve_profile_from_args(args)
        cmd_hot_reload(args.target, profile=profile_name, verbose=args.verbose)
    elif args.command == "exec":
        cmd_exec(args.command_args, args.target)
    elif args.command == "audit":
        cmd_audit(args.target, args.json)
    elif args.command == "outdated":
        cmd_outdated(args.target, args.json)
    elif args.command == "sbom":
        cmd_sbom(args.target, args.format, args.output)
    elif args.command == "doctor":
        cmd_doctor(args.target, args.json)
    elif args.command == "self-update":
        cmd_self_update(args.check, args.yes)
    elif args.command == "completions":
        cmd_completions(args.shell)
    elif args.command == "complete-targets":
        cmd_complete_targets()
    elif args.command == "git":
        cmd_git()
    elif args.command == "run":
        profile_name = resolve_profile_from_args(args)
        cmd_run(args.target, entry_file=args.entry_file, profile=profile_name)
    elif args.command == "test":
        profile_name = resolve_profile_from_args(args)
        if args.all:
            config = load_config_or_exit()
            run_across_workspace(config, lambda: cmd_test(None, profile=profile_name, verbose=args.verbose))
        else:
            cmd_test(args.target, profile=profile_name, verbose=args.verbose)
    elif args.command == "add":
        cmd_add_dep(args.packages, args.target)
    elif args.command == "remove":
        cmd_remove_dep(args.packages, args.target)
    elif args.command == "ide-sync":
        cmd_ide_sync()