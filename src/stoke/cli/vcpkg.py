"""vcpkg 관련 명령어."""
import sys
from stoke.cli.utils import load_config_or_exit

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
    """stoke vcpkg install <library> [--version=X] [--target=Y]"""
    from stoke.vcpkg import install_library
    from stoke.c_libraries import can_use_in_c_project
    from stoke.toml_editor import add_dep

    config = load_config_or_exit()

    if target is None:
        target = next(iter(config.targets))
        print(f"No target specified, using: {target}")

    if target not in config.targets:
        print(f"Error: target '{target}' not found in stoke.toml", file=sys.stderr)
        print(f"Available targets: {', '.join(config.targets.keys())}", file=sys.stderr)
        sys.exit(1)

    target_config = config.targets[target]

    if target_config.language not in ("c", "cpp"):
        print(
            f"Error: vcpkg is only for C/C++ projects.\n"
            f"  Target '{target}' is a {target_config.language} project.",
            file=sys.stderr,
        )
        sys.exit(1)

    if target_config.language == "c":
        if not can_use_in_c_project(library):
            print(
                f"Error: '{library}' is not a C library.\n"
                f"  C project '{target}' cannot use it.\n"
                f"  Consider using a C++ project or a C alternative.",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        install_library(library, version)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    stoke_toml_path = config.config_path
    version_str = version if version else "latest"
    try:
        add_dep(stoke_toml_path, target, library, version_str)
        print(f"\nAdded to stoke.toml: {library} = \"{version_str}\"")
    except (OSError, ValueError) as e:
        print(f"Warning: library installed but failed to update stoke.toml: {e}", file=sys.stderr)


def cmd_vcpkg_remove_library(library: str, target: str | None):
    """stoke vcpkg remove <library> [--target=Y]"""
    from stoke.vcpkg import remove_library
    from stoke.toml_editor import remove_dep

    config = load_config_or_exit()

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

    stoke_toml_path = config.config_path
    try:
        removed = remove_dep(stoke_toml_path, target, library)
        if not removed:
            print(f"Warning: '{library}' not found in stoke.toml deps")
    except (OSError, ValueError) as e:
        print(f"Error updating stoke.toml: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        remove_library(library)
    except RuntimeError as e:
        print(f"Warning: vcpkg remove failed: {e}", file=sys.stderr)

    print(f"\nRemoved from stoke.toml: {library}")


def cmd_vcpkg_list_libraries(target: str | None):
    """stoke vcpkg list [--target=Y]"""
    from stoke.toml_editor import list_deps

    config = load_config_or_exit()

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