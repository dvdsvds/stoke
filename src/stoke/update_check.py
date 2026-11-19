"""새 버전 알림 -- 명령이 끝난 뒤 stderr에 한 줄만 안내. 설치는 하지 않고 `stoke self-update`를 가리킴.

조회는 self_update.fetch_latest(GitHub 최신 릴리스)를 그대로 씀.
- 24시간에 한 번만 조회하고 결과를 캐시 (사용자 캐시 폴더의 update-check.json, 몇 줄짜리 파일).
- 짧은 타임아웃, 실패(오프라인 등)하면 조용히 넘어감. 어떤 경우에도 명령 자체를 막거나 실패시키지 않음.
- 같은 안내는 24시간에 한 번만 출력.
- 보내는 정보 없음: 공개 API에 GET 한 번 (사용자·프로젝트 정보 없이 일반 User-Agent만).
- 끄기: STOKE_NO_UPDATE_CHECK=1. CI 환경이거나 stderr가 터미널이 아니면(파이프/리다이렉트) 자동으로 꺼짐.
"""
import json
import os
import sys
import time
from pathlib import Path

from stoke import __version__

_CHECK_INTERVAL = 24 * 3600
_TIMEOUT = 1.5
# 출력이 셸에 eval되거나, 자동완성 훅으로 자주 호출되거나, 이미 업데이트를 다루는 명령은 건너뜀
_SKIP_COMMANDS = {"env", "self-update", "completions", "complete-targets"}

def _cache_path() -> Path:
    override = os.environ.get("STOKE_CACHE_DIR")
    if override:
        base = Path(override)
    elif sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "stoke"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "stoke"
    return base / "update-check.json"

def _load_state() -> dict:
    try:
        data = json.loads(_cache_path().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}

def _save_state(state: dict) -> None:
    try:
        path = _cache_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass

def _fetch_latest_version() -> str:
    from stoke.self_update import fetch_latest
    return fetch_latest(timeout=_TIMEOUT).version

def _disabled(command: str | None) -> bool:
    return (
        bool(os.environ.get("STOKE_NO_UPDATE_CHECK"))
        or bool(os.environ.get("CI"))
        or command in _SKIP_COMMANDS
        or not sys.stderr.isatty()
    )

def maybe_notify(command: str | None = None) -> None:
    try:
        if _disabled(command):
            return

        from stoke.self_update import is_newer

        state = _load_state()
        now = time.time()

        if now - state.get("checked_at", 0) >= _CHECK_INTERVAL:
            try:
                state["latest"] = _fetch_latest_version()
            except Exception:
                pass  # 오프라인·제한 등: 이전 값 유지, 다음 날 다시 시도
            state["checked_at"] = now
            _save_state(state)

        latest = state.get("latest")
        if (latest and is_newer(latest, __version__)
                and now - state.get("notified_at", 0) >= _CHECK_INTERVAL):
            print(
                f"\nstoke {latest} is available (you have {__version__}). Update with: stoke self-update\n"
                f"  (silence this with STOKE_NO_UPDATE_CHECK=1)",
                file=sys.stderr,
            )
            state["notified_at"] = now
            _save_state(state)
    except Exception:
        # 알림은 부가 기능 - 무슨 일이 있어도 본 명령에 영향 주지 않음
        pass
