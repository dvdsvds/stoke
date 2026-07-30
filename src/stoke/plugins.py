"""
플러그인 시스템: 언어/프레임워크를 stoke 소스 수정 없이 외부 패키지로 추가.

설치된 패키지가 자기 pyproject.toml에 entry point를 등록하면 stoke가 자동 인식함.

언어 플러그인 (빌드/실행/watch/hot-reload 지원 추가):
    [project.entry-points."stoke.languages"]
    mylang = "my_package.stoke_plugin:MYLANG_PLUGIN"

    "my_package.stoke_plugin" 모듈에 다음이 있어야 함:
    MYLANG_PLUGIN = LanguagePlugin(
        make_adapter=lambda target, project, project_root, profile=None, verbose=False: MyLangAdapter(...),
        source_extensions={".mylang"},
    )

프레임워크 플러그인 (`stoke init <name>` 스캐폴드 추가):
    [project.entry-points."stoke.frameworks"]
    my-framework = "my_package.stoke_plugin:cmd_init_my_framework"

    "cmd_init_my_framework"는 인자 없이 호출되는 콜러블이어야 함 (기존
    cmd_init_fastapi 등과 동일한 계약 -- cwd 기준으로 직접 파일을 씀).
"""
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
