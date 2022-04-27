from typing import List, Union

from aiohttp import ClientSession, ServerTimeoutError, ClientResponseError, ContentTypeError
from nonebot import logger
from pydantic import BaseModel


class Tag(BaseModel):
    label: str
    color: str


class Plugin(BaseModel):
    module_name: str
    project_link: str
    name: str
    desc: str
    author: str
    homepage: str
    tags: List[Tag]
    is_official: bool


async def get_plugins_list(url: str) -> Union[List[Plugin], None]:
    logger.trace("Get plugins list")
    async with ClientSession() as session:
        try:
            plugins = []
            resp = await session.get(url)
            resp.raise_for_status()
            data = await resp.json()
            for i in data:
                plugins.append(Plugin.parse_obj(i))
            return plugins
        except ServerTimeoutError or ClientResponseError or ContentTypeError:
            logger.warning("Can't get plugins list, please check network")
            return None


async def get_author_avatars(user_name: str) -> Union[str, None]:
    # will use in near future
    logger.trace(f"Get user {user_name}'s avatars")
    async with ClientSession() as session:
        try:
            resp = await session.get(f"https://api.github.com/users/{user_name}")
            resp.raise_for_status()
            return (await resp.json()).get("avatar_url")
        except ServerTimeoutError or ClientResponseError or ContentTypeError:
            logger.warning(f"Can't get {user_name}'s avatar, please check network")
            return None
