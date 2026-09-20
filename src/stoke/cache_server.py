"""stoke cache-server -- STOKE_REMOTE_CACHE_URL이 기대하는 프로토콜(GET/PUT /objects/<key>, /dirs/<key>.tar)의
레퍼런스 구현. 파일시스템 뒤에 얹은 아주 단순한 키-값 blob 저장소 -- 컴파일 결과물은 소스만 있으면 언제든
다시 만들 수 있는 파생물이라, 별도 DB나 정합성 보장 없이 "있으면 쓰고 없으면 미스" 수준이면 충분함.

기본으로 안전하게: 인증 필수, localhost 바인딩 기본값, 업로드 크기 제한, 한 번 쓴 키는 덮어쓰기 거부(write-once).
"""
import base64
import http.server
import socketserver
import ssl
import sys
from pathlib import Path

_DEFAULT_MAX_UPLOAD_BYTES = 200 * 1024 * 1024  # 200MB

class _CacheHandler(http.server.BaseHTTPRequestHandler):
    # 서브클래스에서 채워짐
    cache_dir: Path
    auth: tuple[str, str]
    max_upload_bytes: int

    def log_message(self, format: str, *args) -> None:
        sys.stderr.write(f"{self.address_string()} - {format % args}\n")

    def _authorized(self) -> bool:
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(header[len("Basic "):]).decode("utf-8")
            user, _, password = decoded.partition(":")
        except Exception:
            return False
        return (user, password) == self.auth

    def _require_auth(self) -> bool:
        if self._authorized():
            return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="stoke-cache-server"')
        self.end_headers()
        return False

    def _safe_path(self) -> Path | None:
        """object/dirs 경로만 허용, 상위 디렉토리 탈출(zip-slip류) 방지."""
        rel = self.path.lstrip("/")
        if not (rel.startswith("objects/") or rel.startswith("dirs/")):
            return None
        target = (self.cache_dir / rel).resolve()
        if not target.is_relative_to(self.cache_dir.resolve()):
            return None
        return target

    def do_GET(self) -> None:
        if not self._require_auth():
            return
        path = self._safe_path()
        if path is None or not path.is_file():
            self.send_response(404)
            self.end_headers()
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_PUT(self) -> None:
        if not self._require_auth():
            return
        path = self._safe_path()
        if path is None:
            self.send_response(400)
            self.end_headers()
            return

        # write-once: 이미 있는 키는 절대 덮어쓰지 않음 -- 정상적으로 채워진 캐시 항목을
        # 나중에 악성 내용으로 바꿔치기하는 걸 막는 최소한의 방어선.
        if path.exists():
            self.send_response(409)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        if length > self.max_upload_bytes:
            self.send_response(413)
            self.end_headers()
            return

        data = self.rfile.read(length)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + f".tmp-{id(self)}")
        tmp.write_bytes(data)

        # 두 요청이 같은 키에 동시에 도착하는 경합 대비, rename 직전에 한 번 더 확인.
        if path.exists():
            tmp.unlink(missing_ok=True)
            self.send_response(409)
            self.end_headers()
            return

        tmp.replace(path)
        self.send_response(200)
        self.end_headers()

class _ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run_cache_server(
    port: int,
    directory: Path,
    user: str,
    password: str,
    host: str = "127.0.0.1",
    cert: Path | None = None,
    key: Path | None = None,
    max_upload_bytes: int = _DEFAULT_MAX_UPLOAD_BYTES,
) -> None:
    directory.mkdir(parents=True, exist_ok=True)

    handler = type("BoundCacheHandler", (_CacheHandler,), {
        "cache_dir": directory,
        "auth": (user, password),
        "max_upload_bytes": max_upload_bytes,
    })

    server = _ThreadingServer((host, port), handler)
    if cert and key:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        scheme = "https"
    else:
        scheme = "http"

    print(f"stoke cache-server listening on {scheme}://{host}:{port}, storing in {directory}")
    print("Basic Auth required.")
    if scheme == "http" and host not in ("127.0.0.1", "localhost", "::1"):
        print(
            "Warning: serving plain HTTP on a non-localhost address -- credentials and cache "
            "contents travel unencrypted. Pass --cert/--key, or put this behind a TLS-terminating "
            "reverse proxy.",
            file=sys.stderr,
        )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
