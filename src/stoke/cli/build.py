"""빌드, 실행, watch, hot-reload 명령어."""
import sys
from stoke.adapters import make_adapter
from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit, check_profile_or_exit

def cmd_build(target_name, force: bool = False, profile: str = "debug", verbose: bool = False):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    target_name = resolve_target_or_exit(config, target_name, verb="using", verbose=verbose)
    target = config.targets[target_name]
    if force:
        print(f"Building '{target.name}' ({target.language}) [force rebuild]...")
    else:
        print(f"Building '{target.name}' ({target.language})...")

    project_root = config.config_path.parent
    try:
        profile_obj = config.profiles[profile]
        adapter = make_adapter(target, config.project, project_root, profile=profile_obj, verbose=verbose)
        adapter.build(force=force)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_run(target_name, profile: str = "debug"):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    # run은 verbose=True로 항상 표시 (기존 동작 유지)
    target_name = resolve_target_or_exit(config, target_name, verb="running", verbose=True)
    target = config.targets[target_name]
    project_root = config.config_path.parent

    try:
        profile_obj = config.profiles[profile]
        adapter = make_adapter(target, config.project, project_root, profile=profile_obj)
        exit_code = adapter.run()
        sys.exit(exit_code)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_watch(target_name, profile: str = "debug", verbose: bool = False):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    target_name = resolve_target_or_exit(config, target_name, verb="watching", verbose=verbose)
    target = config.targets[target_name]
    project_root = config.config_path.parent
    profile_obj = config.profiles[profile]

    from stoke.watcher import watch

    try:
        watch(target, config, project_root, profile=profile_obj, verbose=verbose)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def cmd_hot_reload(target_name, profile: str = "debug", verbose: bool = False):
    config = load_config_or_exit()
    check_profile_or_exit(config, profile)
    target_name = resolve_target_or_exit(config, target_name, verb="hot-reloading", verbose=verbose)
    target = config.targets[target_name]

    project_root = config.config_path.parent
    profile_obj = config.profiles[profile]

    from stoke.hot_reload import hot_reload

    try:
        hot_reload(target, config, project_root, profile=profile_obj, verbose=verbose)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)