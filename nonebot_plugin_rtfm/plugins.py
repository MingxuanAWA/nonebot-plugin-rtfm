from difflib import SequenceMatcher
from typing import List, Union, Dict, Callable, Optional

from aiohttp import ClientSession, ClientResponseError, ContentTypeError, ClientConnectorError
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

    def __hash__(self):
        return hash(self.module_name)

    def __eq__(self, other):
        return self.module_name == other.module_name


Plugins = List[Plugin]


class Index:
    def __init__(self, plugins: Plugins):
        self.plugins = plugins
        self.tags: Dict[str, Plugins] = dict()
        self.name: Dict[str, Plugins] = dict()
        self.desc: Dict[str, Plugins] = dict()
        self.author: Dict[str, Plugins] = dict()
        self.module_name: Dict[str, Plugins] = dict()

        tags = self.tags
        names = self.name
        desc = self.desc
        author = self.author
        module_name = self.module_name
        for i in plugins:
            for tag in i.tags:
                if dict_tag := tags.get(tag.label):
                    dict_tag.append(i)
                else:
                    tags.update({tag.label: [i]})

            if dict_tag := names.get(i.name):
                dict_tag.append(i)
            else:
                names.update({i.name: [i]})

            if dict_tag := desc.get(i.desc):
                dict_tag.append(i)
            else:
                desc.update({i.desc: [i]})

            if dict_tag := author.get(i.author):
                dict_tag.append(i)
            else:
                author.update({i.author: [i]})

            if dict_tag := module_name.get(i.module_name):
                dict_tag.append(i)
            else:
                module_name.update({i.module_name: [i]})

    @staticmethod
    def base_search(source: str, diff: str, plugins: Dict[str, Plugins],
                    percent: float = 0.6, is_junk: Optional[Callable] = None) -> Plugins:
        result_plugins: Plugins = []
        sequence = SequenceMatcher(a=source, b=diff, isjunk=is_junk)
        if sequence.ratio() > percent:
            result_plugins += plugins.get(source, [])
        return result_plugins

    def get_plugins(self):
        return self.plugins

    def search_by_tags(self, tag: str, percent: Optional[float] = 0.6) -> Plugins:
        plugins: Plugins = []
        for i in self.tags:
            plugins += self.base_search(i, tag, self.tags, percent, lambda s: s in ["t:", "a:"])
        return plugins

    def search_by_name(self, name: str, percent: Optional[float] = 0.6) -> Plugins:
        plugins: Plugins = []
        for i in self.name:
            plugins += self.base_search(i, name, self.name, percent)
        return plugins

    def search_by_author(self, author: str, percent: Optional[float] = 0.7) -> Plugins:
        plugins: Plugins = []
        for i in self.author:
            plugins += self.base_search(i, author, self.author, percent)
        return plugins

    def search_by_desc(self, desc: str, percent: Optional[float] = 0.02) -> Plugins:
        plugins: Plugins = []
        for i in self.desc:
            plugins += self.base_search(i, desc, self.desc, percent)
        return plugins


async def get_plugins_list(url: str) -> Union[Plugins, None]:
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
        except ClientConnectorError or ClientResponseError or ContentTypeError:
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
        except ClientConnectorError or ClientResponseError or ContentTypeError:
            logger.warning(f"Can't get {user_name}'s avatar, please check network")
            return None
