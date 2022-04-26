from typing import TYPE_CHECKING

import pytest
from nonebug import App

if TYPE_CHECKING:
    from nonebot.plugin import Plugin


@pytest.fixture()
async def init_plugin(app: App) -> "Plugin":
    import nonebot

    return nonebot.load_plugin("nonebot_plugin_rtfm")
