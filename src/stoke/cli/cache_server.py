"""stoke cache-server -- CLI 진입점."""
import sys
from pathlib import Path

from stoke.cache_server import run_cache_server

def cmd_cache_server(
    port: int,
    directory: str,
    user: str | None,
    password: str | None,
    host: str,
    cert: str | None,
    key: str | None,
    max_upload_mb: int,
) -> None:
    """stoke cache-server -- STOKE_REMOTE_CACHE_URL용 레퍼런스 서버. --user/--password는 필수."""
    if not user or not password:
        print(
            "Error: --user and --password are required (no anonymous-write mode) -- \n"
            "  this server would otherwise let anyone on the network read and poison the cache.",
            file=sys.stderr,
        )
        sys.exit(1)

    if bool(cert) != bool(key):
        print("Error: --cert and --key must be given together.", file=sys.stderr)
        sys.exit(1)

    run_cache_server(
        port=port,
        directory=Path(directory),
        user=user,
        password=password,
        host=host,
        cert=Path(cert) if cert else None,
        key=Path(key) if key else None,
        max_upload_bytes=max_upload_mb * 1024 * 1024,
    )
