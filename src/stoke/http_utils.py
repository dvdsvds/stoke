"""공용 HTTP 헬퍼 (인증 헤더 등)."""
import base64

def basic_auth_headers(username: str | None, password: str | None) -> dict[str, str]:
    """HTTP Basic Auth 헤더 생성 (username 없으면 빈 dict; URL에 credential은 안 끼워넣음)."""
    if not username:
        return {}
    credentials = f"{username}:{password or ''}"
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {encoded}"}
