"""CLI 헬퍼 유틸리티."""
import sys
from stoke.config import load_config, Config
from stoke.cli.messages import get_message as _

def resolve_profile_from_args(args) -> str:
    """
    --debug / --release / --profile 옵션에서 프로파일 이름 결정.
    충돌 시 SystemExit.
    """
    if args.debug and args.release:
        print("Error: cannot use both --debug and --release", file=sys.stderr)
        sys.exit(1)
    if (args.debug or args.release) and args.profile:
        flag_name = "--debug" if args.debug else "--release"
        print(f"Error: cannot use {flag_name} with --profile", file=sys.stderr)
        sys.exit(1)

    if args.release:
        return "release"
    elif args.profile:
        return args.profile
    else:
        return "debug"

def add_debug_release_profile_args(subparser, command_name: str, include_verbose: bool = True) -> None:
    """build/watch/run/hot-reload가 공통으로 쓰는 --debug/--release/--profile[/-v] 인자 추가"""
    subparser.add_argument("--debug", action="store_true", help=_(f"{command_name}.debug"))
    subparser.add_argument("--release", action="store_true", help=_(f"{command_name}.release"))
    subparser.add_argument("--profile", default=None, help=_(f"{command_name}.profile"))
    if include_verbose:
        subparser.add_argument("-v", "--verbose", action="store_true", help=_(f"{command_name}.verbose"))

def load_config_or_exit() -> Config:
    """stoke.toml 로드. 실패 시 에러 출력 후 종료."""
    try:
        return load_config()
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def resolve_target_or_exit(
    config: Config,
    target_name: str | None,
    verb: str = "using",
    verbose: bool = False,
) -> str:
    """
    타겟 이름 결정. 없으면 첫 번째 타겟 사용.
    존재하지 않으면 에러 종료.
    verb: "using", "running", "watching", "hot-reloading" 등
    """
    if target_name is None:
        target_name = next(iter(config.targets))
        if verbose:
            print(f"No target specified, {verb} default: {target_name}")

    if target_name not in config.targets:
        print(f"Error: target '{target_name}' not found in stoke.toml", file=sys.stderr)
        print(f"Available targets: {', '.join(config.targets.keys())}", file=sys.stderr)
        sys.exit(1)

    return target_name

def check_profile_or_exit(config: Config, profile: str):
    """프로파일 존재 확인. 없으면 에러 종료."""
    if profile not in config.profiles:
        print(f"Error: profile '{profile}' not found", file=sys.stderr)
        print(f"Available profiles: {', '.join(config.profiles.keys())}", file=sys.stderr)
        sys.exit(1)

def resolve_cpp_target(config: Config, target_name: str | None, *, announce: bool = True, show_available: bool = True):
    """vcpkg 명령어 전용 타겟 해석: 기본 타겟 선택 -> 존재 확인 -> c/cpp 언어 확인"""
    if target_name is None:
        target_name = next(iter(config.targets))
        if announce:
            print(f"No target specified, using: {target_name}")

    if target_name not in config.targets:
        print(f"Error: target '{target_name}' not found in stoke.toml", file=sys.stderr)
        if show_available:
            print(f"Available targets: {', '.join(config.targets.keys())}", file=sys.stderr)
        sys.exit(1)

    target_config = config.targets[target_name]
    if target_config.language not in ("c", "cpp"):
        print(
            f"Error: vcpkg is only for C/C++ projects.\n"
            f"  Target '{target_name}' is a {target_config.language} project.",
            file=sys.stderr,
        )
        sys.exit(1)
    return target_config