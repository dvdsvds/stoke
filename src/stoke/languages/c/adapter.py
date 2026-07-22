"""C 언어 어댑터. gcc 사용."""

from stoke.languages.c.base import CBaseAdapter

class CAdapter(CBaseAdapter):
    compiler_kind = "c"
    source_extension = ".c"
    default_standard = "c17"

    def _get_standard(self) -> str | None:
        """stoke.toml의 c_standard 사용. 없으면 None (컴파일러 기본값)."""
        return self.target.c_standard