"""stoke self-update -- CLI 진입점."""
import sys

from stoke import __version__
from stoke.prompts import _prompt_yes_no
from stoke.self_update import (
    apply_update_unix,
    apply_update_windows,
    fetch_latest,
    is_frozen,
    is_newer,
    _install_dir,
    _platform_asset_name,
)

def cmd_self_update(check_only: bool, yes: bool) -> None:
    if not is_frozen():
        print(
            "Error: 'stoke self-update' only works for the standalone binary distribution "
            "(you're running stoke from source).",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Current version: {__version__}")
    try:
        latest = fetch_latest()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not is_newer(latest.version, __version__):
        print(f"Already up to date (latest: {latest.version}).")
        return

    print(f"Latest version: {latest.version}")

    if check_only:
        print(f"Run 'stoke self-update' to install it.")
        return

    asset_name = _platform_asset_name(latest.version)
    url = latest.assets.get(asset_name) if asset_name else None
    if url is None:
        print(
            f"Error: no release asset found for this platform"
            f"{f' ({asset_name})' if asset_name else ''}.\n"
            f"  See: https://github.com/dvdsvds/stoke/releases/tag/v{latest.version}",
            file=sys.stderr,
        )
        sys.exit(1)

    if not yes and not _prompt_yes_no(f"Update stoke {__version__} -> {latest.version}?", default=True):
        print("Cancelled.")
        return

    print(f"Downloading {asset_name}...")
    try:
        if sys.platform == "win32":
            apply_update_windows(url)
            print("Update started in the background. It may take a few seconds to finish.")
            print("Open a new terminal afterwards to use the updated version.")
        else:
            apply_update_unix(url, _install_dir())
            print(f"Updated to {latest.version}. Restart stoke to use the new version.")
    except Exception as e:
        print(f"Error applying update: {e}", file=sys.stderr)
        sys.exit(1)
