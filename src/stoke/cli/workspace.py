"""stoke build/test --all -- 워크스페이스 루트에서 members를 순회하며 각자 디렉토리에서 명령 실행."""
import os
import sys
from pathlib import Path

def run_across_workspace(config, runner) -> None:
    """config가 워크스페이스 루트여야 함. 각 member 디렉토리로 chdir해서 runner()를 실행 (SystemExit는 잡아서 계속 진행)."""
    if config.workspace is None:
        print(
            "Error: --all requires a workspace root (run 'stoke init --workspace' first, "
            "or run this command inside a single service directory instead).",
            file=sys.stderr,
        )
        sys.exit(1)

    members = config.workspace.members
    if not members:
        print("Workspace has no members yet -- add one with 'stoke new <name> -l <language>'.")
        return

    root = config.config_path.parent
    original_cwd = Path.cwd()
    failed = []

    for member in members:
        member_dir = root / member
        print(f"\n=== {member} ===")

        if not (member_dir / "stoke.toml").exists():
            print(f"Error: {member_dir / 'stoke.toml'} not found, skipping", file=sys.stderr)
            failed.append(member)
            continue

        try:
            os.chdir(member_dir)
            runner()
        except SystemExit as e:
            code = e.code
            if code not in (None, 0):
                failed.append(member)
        finally:
            os.chdir(original_cwd)

    print()
    if failed:
        print(f"{len(failed)}/{len(members)} member(s) failed: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
    print(f"All {len(members)} member(s) succeeded.")
