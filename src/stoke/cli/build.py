"""빌드, 실행, watch, hot-reload 명령어."""
import sys
from stoke.config import load_config
from stoke.adapters import make_adapter


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
    try:
        profile_obj = config.profiles[profile]
        adapter = make_adapter(target, config.project, project_root, profile=profile_obj)
        exit_code = adapter.run()
        sys.exit(exit_code)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_watch(target_name, profile: str = "debug", verbose: bool = False):
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
    profile_obj = config.profiles[profile]
    from stoke.watcher import watch
    try:
        watch(target, config, project_root, profile=profile_obj, verbose=verbose)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_hot_reload(target_name, profile: str = "debug", verbose: bool = False):
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
    profile_obj = config.profiles[profile]
    from stoke.hot_reload import hot_reload
    try:
        hot_reload(target, config, project_root, profile=profile_obj, verbose=verbose)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)