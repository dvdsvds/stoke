from pathlib import Path

def write_if_changed(path: Path, content: str) -> bool:
    """content가 기존과 다를 때만 write. 실제로 썼으면 True"""
    if path.exists():
        if path.read_text(encoding="utf-8") == content:
            return False
    path.write_text(content, encoding="utf-8")
    return True