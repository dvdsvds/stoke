"""CLI 헬퍼 유틸리티."""
import sys

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