"""플러그인 시스템: 외부 패키지가 pyproject.toml entry point로 언어/프레임워크를 등록."""
from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import entry_points
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from stoke.adapters.base import BaseAdapter

LANGUAGE_GROUP = "stoke.languages"
FRAMEWORK_GROUP = "stoke.frameworks"


@dataclass(frozen=True)
class LanguagePlugin:
    """언어 플러그인이 구현해야 하는 인터페이스."""
    make_adapter: Callable[..., "BaseAdapter"]
    source_extensions: set[str]


_language_plugins: dict[str, LanguagePlugin] | None = None
_framework_plugins: dict[str, Callable[[], None]] | None = None


def _load_language_plugins() -> dict[str, LanguagePlugin]:
    global _language_plugins
    if _language_plugins is None:
        _language_plugins = {
            ep.name: ep.load() for ep in entry_points(group=LANGUAGE_GROUP)
        }
    return _language_plugins


def _load_framework_plugins() -> dict[str, Callable[[], None]]:
    global _framework_plugins
    if _framework_plugins is None:
        _framework_plugins = {
            ep.name: ep.load() for ep in entry_points(group=FRAMEWORK_GROUP)
        }
    return _framework_plugins


def get_language_plugin(name: str) -> LanguagePlugin | None:
    return _load_language_plugins().get(name)


def all_language_plugin_names() -> list[str]:
    return list(_load_language_plugins().keys())


def get_framework_plugin(name: str) -> Callable[[], None] | None:
    return _load_framework_plugins().get(name)


def all_framework_plugin_names() -> list[str]:
    return list(_load_framework_plugins().keys())
