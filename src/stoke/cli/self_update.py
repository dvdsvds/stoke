"""stoke self-update -- CLI 진입점. 설치 방식(frozen/editable/pip)에 따라 실제 업데이트 방법이 갈림."""
import sys

from stoke import __version__
from stoke.prompts import _prompt_yes_no
from stoke.self_update import (
    apply_update_unix,
    apply_update_windows,
    detect_install_method,
    fetch_latest,
    is_newer,
    update_editable_install,
    update_pip_install,
    _install_dir,
    _platform_asset_name,
)

def _update_frozen(latest, yes: bool) -> None:
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

def _update_editable(latest, yes: bool) -> None:
    if not yes and not _prompt_yes_no(f"git pull the stoke checkout to update {__version__} -> {latest.version}?", default=True):
        print("Cancelled.")
        return
    ok, message = update_editable_install()
    if ok:
        print(message)
        print("Restart stoke to use the new version.")
    else:
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)

def _update_pip(latest, yes: bool) -> None:
    if not yes and not _prompt_yes_no(f"pip install --upgrade stoke {__version__} -> {latest.version}?", default=True):
        print("Cancelled.")
        return
    print("Running pip install --upgrade...")
    ok, message = update_pip_install(latest.version)
    if ok:
        print(message)
        print("Restart stoke to use the new version.")
    else:
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)

def cmd_self_update(check_only: bool, yes: bool) -> None:
    method = detect_install_method()
    if method == "unknown":
        print(
            "Error: couldn't figure out how stoke was installed here, so 'stoke self-update' "
            "doesn't know what to update.\n"
            f"  Check manually: https://github.com/dvdsvds/stoke/releases/latest",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Current version: {__version__} ({method} install)")
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

    if method == "frozen":
        _update_frozen(latest, yes)
    elif method == "editable":
        _update_editable(latest, yes)
    else:
        _update_pip(latest, yes)
