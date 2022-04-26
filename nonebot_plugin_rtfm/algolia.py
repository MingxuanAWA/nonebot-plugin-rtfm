from re import sub
from typing import Set

from algoliasearch.search_client import SearchClient

KEYWORD = {
    "class-var ": "类变量 ",
    "class ": "类 ",
    "def ": "函数 ",
    "method ": "方法 ",
    "module ": "模块 ",
    "package ": "包 ",
    "property ": "属性 ",
    "static ": "静态 ",
    "async ": "异步 ",
    "abstract ": "抽象 "
}


class SearchResult:

    def translate_keyword(self):
        for i in KEYWORD:
            self.sub_title = self.sub_title.replace(str(i), KEYWORD[i])

    @staticmethod
    def replace(url):
        return url.replace("/next", "").replace(".html", "")

    @staticmethod
    def unescape(text: str):
        return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

    def __init__(self, url: str, parent_url: str, min_title_level: str, sub_title: str, title: str, id_: str,
                 content: str = None):
        self.url = self.replace(url)
        self.parent_url = self.replace(parent_url)
        self.min_title_level = self.unescape(min_title_level)
        self.sub_title = self.unescape(sub_title)
        self.title = self.unescape(title)
        self.content = self.unescape(content) if content else None
        self.id = sub(r"\d+-", "", self.replace(id_))  # in the most cases, `id` is the same as `parent_url`

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


async def search(query: str, app_id: str, api_key: str, index: str) -> Set[SearchResult]:
    result = set()
    async with SearchClient.create(app_id, api_key) as client:
        index = client.init_index(index)
        search_result = await index.search_async(query)

        if not search_result.get("hits"):
            return set()
        for i in search_result["hits"]:
            hierarchy = i["hierarchy"]
            type_ = i["type"]
            if type_ == "content":
                for j in list(hierarchy)[::-1][3:]:  # lvl4, lvl3, lvl2, lvl1
                    if hierarchy[j]:
                        type_ = str(j)
                        min_title = hierarchy[type_]
                        content = i["content"]
                        break
            else:
                min_title = hierarchy[type_]
                content = None
            result.add(SearchResult(i["url"], i["url_without_anchor"], type_,
                                    min_title, hierarchy["lvl1"], i["objectID"], content))
        return result
