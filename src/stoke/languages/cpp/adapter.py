"""C++ 어댑터. g++ 사용."""

from stoke.languages.c.base import CBaseAdapter

class CppAdapter(CBaseAdapter):
    compiler_kind = "cpp"
    source_extension = ".cpp"
    default_standard = "c++17"

    def _get_standard(self) -> str | None:
        """stoke.toml의 cpp_standard 사용. 없으면 None."""
        return self.target.cpp_standard