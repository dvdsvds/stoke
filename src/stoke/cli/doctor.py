"""stoke doctor -- 환경 진단 결과를 사람이 읽기 좋게(또는 --json으로 기계가 읽기 좋게) 출력."""
import json
import sys

from stoke.cli.utils import load_config_or_exit, resolve_target_or_exit
from stoke.doctor import run_checks

_ICON = {"ok": "✓", "warn": "!", "error": "✗"}

def cmd_doctor(target_name: str | None, json_output: bool = False) -> None:
    """stoke doctor [--target=X] [--json] -- stoke build처럼 실제로 뭘 하진 않고, 빠르게 환경만 점검."""
    config = load_config_or_exit()
    target_name = resolve_target_or_exit(config, target_name, verb="checking")
    target = config.targets[target_name]

    results = run_checks(config, target)
    error_count = sum(1 for r in results if r.level == "error")
    warn_count = sum(1 for r in results if r.level == "warn")

    if json_output:
        print(json.dumps({
            "target": target_name,
            "language": target.language,
            "checks": [{"level": r.level, "message": r.message} for r in results],
            "error_count": error_count,
            "warning_count": warn_count,
        }, indent=2))
        sys.exit(1 if error_count else 0)

    print(f"Checking '{target_name}' ({target.language})...\n")
    for result in results:
        print(f"  [{_ICON[result.level]}] {result.message}")

    print()
    if error_count == 0 and warn_count == 0:
        print("Everything looks good.")
    else:
        print(f"{error_count} error(s), {warn_count} warning(s).")

    sys.exit(1 if error_count else 0)
