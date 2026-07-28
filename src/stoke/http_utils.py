"""공용 HTTP 헬퍼 (인증 헤더 등)."""
import base64

def basic_auth_headers(username: str | None, password: str | None) -> dict[str, str]:
    """
    HTTP Basic Auth 헤더 생성.
    username이 없으면 빈 dict 반환 (인증 정보 없이 익명 요청, 기존 동작과 동일한 하위 호환).
    URL에 credential을 끼워넣지 않는 이유: 로그/에러 메시지에 URL이 그대로 찍히는 곳이
    여러 군데라, user:pass@host 방식은 비밀번호가 노출될 위험이 있음.
    """
    if not username:
        return {}
    credentials = f"{username}:{password or ''}"
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("ascii")
    return {"Authorization": f"Basic {encoded}"}
