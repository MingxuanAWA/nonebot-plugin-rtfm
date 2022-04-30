from argparse import Namespace as BaseNamespace
from typing import Set, List, Union, Optional

from nonebot import on_command, get_driver, on_notice, logger, on_shell_command
from nonebot.adapters.onebot.v11 import Message, Event, MessageEvent, MessageSegment, PokeNotifyEvent
from nonebot.exception import ParserExit
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import ArgPlainText, Depends
from nonebot.params import CommandArg, ShellCommandArgs

from .algolia import search, SearchResult
from .config import Config
from .parser import parser, Namespace
from .plugins import get_plugins_list as base_get_plugins_list, Plugin, Plugins, Index

# API Key
NONEBOT2_APP_ID = "X0X5UACHZQ"
NONEBOT2_API_KEY = "ac03e1ac2bd0812e2ea38c0cc1ea38c5"
ONEBOT_ADAPTER_APP_ID = "UXS5VZ9AQX"
ONEBOT_ADAPTER_API_KEY = "f1e9e8357ce05e81665c586c978a7661"

# Plugins list urls
GITHUB = "https://raw.githubusercontent.com/nonebot/nonebot2/master/website/static/plugins.json"
JSDELIVR = "https://cdn.jsdelivr.net/gh/nonebot/nonebot2@master/website/static/plugins.json"

# matcher
nonebot2 = on_command("rtfm")
onebot_adapter = on_command("obrtfm")
page_command = on_command("page")
plugins_list = on_command("插件列表")
search_plugins = on_shell_command("搜索插件", parser=parser)

# session and config
plugin_config = Config.parse_obj(get_driver().config)
user_times = {"nonebot2": {}, "onebot_adapter": {}}
next_page_number = dict()
user_pages = dict()
last_use_plugins_list = dict()
index: Index

# nonebot-plugin-help
nonebot2.__help_name__ = "rtfm"
nonebot2.__help_info__ = "搜索 NoneBot2 文档"
plugins_list.__help_name__ = "插件列表"
plugins_list.__help_info__ = "查看商店的所有插件"
onebot_adapter.__help_name__ = "obrtfm"
onebot_adapter.__help_info__ = "搜索 OneBot 适配器 文档"
page_command.__help_name__ = "page"
page_command.__help_info__ = "查看缓存的指定页码的文档"

__help_version__ = "0.2.0"
__help_plugin_name__ = "NoneBot2 文档搜索"
__usage__ = """NoneBot2 文档搜索
命令：
/rtfm [关键字]      搜索 NoneBot2 文档，未输入关键字进入对话模式
/obrtfm [关键字]    搜索 OneBot 适配器 文档，未输入关键字进入对话模式
/page <页码>        查看缓存的指定页码的文档
/插件列表           查看商店的所有插件
操作：戳一戳         查看缓存的下一页文档

示例：
>>> /rtfm get_bots()
搜索到以下结果：
nonebot--函数 get_bot(self_id=None)
https://v2.nonebot.dev/docs/api/index#get_bot

>>> /rtfm
请输入搜索 Nonebot2 文档的关键字
>>> MessageSegment
搜索到以下结果：
1. 处理消息--NoneBot2 中的消息
MessageSegment 是一个 dataclass ，它具有一个类型标识 type，以及一些对应的数据信息 data。
https://v2.nonebot.dev/docs/tutorial/process-message#nonebot2-%E4%B8%AD%E7%9A%84%E6%B6%88%E6%81%AF
2. nonebot.adapters--抽象类 MessageSegment(type, data=<factory>)
https://v2.nonebot.dev/docs/api/adapters/index#MessageSegment
"""

# Message templates
PLUGIN_TEMPLATE = """名称：{name}
模块名：{module_name}
描述：{desc}
作者：{author}
主页：{page}
标签：{tags}"""

# Messages
SEARCH_PLUGIN_HELP = """帮助：
用法：
\t/搜索插件 <关键字> [-t] [-n] [-a] [-d] [-p=[0-1]]

参数：
\t-t，--without_tag 查询时不使用标签查询
\t-n，--without_name 查询时不使用插件名称查询
\t-a，--without_author 查询时不使用作者名查询
\t-d，--without_desc 查询时不使用描述查询
\t-p=[0-1]，--percent=[0-1] 相似度，越接近1相似度越高
"""


async def init_index():
    global index
    _plugins_list = await get_plugins_list()
    if _plugins_list:
        index = Index(_plugins_list)
        logger.success("Build index success")
    else:
        index = None
        logger.error("Can't build index")


get_driver().on_startup(init_index)


async def get_plugins_list() -> Union[Plugins, None]:
    if plugin_config.use_proxy:
        url = JSDELIVR
    else:
        url = GITHUB
    return await base_get_plugins_list(url)


def save_pages(page: Union[Set[SearchResult], Plugins], user_id: int, count: int):
    count -= 1
    user_pages[user_id] = []
    _temp = []
    _count = 0
    if len(page) <= count:
        user_pages[user_id].append(page)
    else:
        for i in page:
            _temp.append(i)
            if _count == count:
                user_pages[user_id].append(_temp[:])
                _temp.clear()
                _count = 0
            else:
                _count += 1
        if _count != 0:
            user_pages[user_id].append(_temp[:])


def save_nonebot_times(event: Event):
    user_id = event.get_user_id()
    last_use_plugins_list[user_id] = True
    user_times["nonebot2"][user_id] = (user_times.get("nonebot2", None)).get(user_id, 0) + 1
    if user_times["nonebot2"][user_id] >= 3:
        user_times["nonebot2"][user_id] = 0
        return 0
    return user_times["nonebot2"][user_id]


def save_onebot_adapter_times(event: Event):
    user_id = event.get_user_id()
    last_use_plugins_list[user_id] = True
    user_times["onebot_adapter"][user_id] = (user_times.get("onebot_adapter", None)).get(user_id, 0) + 1
    if user_times["onebot_adapter"][user_id] >= 3:
        user_times["onebot_adapter"][user_id] = 0
        return 0
    return user_times["onebot_adapter"][user_id]


async def search_manual(keyword: str, name: str, reject_times: int, matcher: Matcher, user_id: int,
                        is_translate: bool = True):
    if name == "NoneBot2":
        app_id, api_key = NONEBOT2_APP_ID, NONEBOT2_API_KEY
        index_name = "nonebot"
    elif name == "OneBot 适配器":
        app_id, api_key = ONEBOT_ADAPTER_APP_ID, ONEBOT_ADAPTER_API_KEY
        index_name = "adapter-onebot"
    else:
        return
    search_result = await search(keyword, app_id, api_key, index_name)
    if not search_result:
        if reject_times == 1:
            await matcher.reject(Message(f"未在 {name} 文档找到 {keyword}，请输入其他关键字"))
        elif reject_times == 2:
            await matcher.reject(Message(f"（最后一次）未在 {name} 文档找到 {keyword}，请输入其他关键字"))
        else:
            await matcher.finish(Message(f"（未在 {name} 文档找到 {keyword}"))
    else:
        msg = "搜索到以下结果：\n"
        if len(search_result) == 1:
            result = search_result.pop()
            if is_translate:
                result.translate_keyword()
            message = [f"{result.title}--{result.sub_title}\n{result.url}"]
            page_number = 1
            next_page_number[user_id] = page_number + 1
            message = Message(
                "\n".join(message) +
                f"\n=== 第 1 页 / 共 {page_number} 页 ==="
                f"\n（使用 /page <页码> 查看指定页）"
            )
        else:
            save_pages(search_result, user_id, plugin_config.rtfm_page)
            next_page_number[user_id] = 2
            message = get_message(user_pages[user_id][0], 1, len(user_pages[user_id]), is_translate) \
                      + "\n（使用 /page <页码> 查看指定页）"
        await matcher.finish(Message(
            msg + message
        ))


def get_message(page: List[SearchResult], page_number: int, max_number: int, is_translate: bool = True) -> Message:
    msg_list = []
    for i, result in enumerate(page):
        if is_translate:
            result.translate_keyword()
        temp_msg = f"{i + 1}. {result.title}--{result.sub_title}\n"
        if result.content:
            temp_msg += f"{result.content}\n"
        temp_msg += f"{result.url}"
        msg_list.append(temp_msg)
    return Message("\n".join(msg_list) + f"\n=== 第 {page_number} 页 / 共 {max_number} 页 ===")


def search_plugins_(keyword: str, no_tags: bool = False, no_name: bool = False, no_author: bool = False,
                    no_desc: bool = False, percent: Optional[float] = None) -> Set[Plugin]:
    _plugins: Plugins = []
    if percent:
        author_percent = desc_percent = percent
    else:
        percent = 0.6
        author_percent = 0.7
        desc_percent = 0.15

    if not no_tags:
        _plugins += index.search_by_tags(keyword, percent)

    if not no_name:
        _plugins += index.search_by_name(keyword, percent)

    if not no_author:
        _plugins += index.search_by_author(keyword, author_percent)

    if not no_desc:
        _plugins += index.search_by_desc(keyword, desc_percent)

    return set(_plugins)


def get_plugins_message(page: Plugins, page_number: int, max_number: int) -> Message:
    msg_list = Message()
    for i, result in enumerate(page):
        tags = [name.label for name in result.tags]
        msg_list.append(
            f"{i + 1}. " + PLUGIN_TEMPLATE.format(
                name=result.name,
                module_name=result.module_name,
                desc=result.desc,
                author=result.author,
                page=result.homepage,
                tags="，".join(tags) if tags else "无"
            ) + ("\n（官方插件）" if result.is_official else "") +
            ("\n" if i + 1 != len(page) else "")
        )
    msg_list.append(
        f"\n=== 第 {page_number} 页 / 共 {max_number} 页 ==="
    )
    return Message(msg_list)


@nonebot2.handle()
async def search_nonebot2_manual(matcher: Matcher, args: Message = CommandArg()):
    """
    搜索 NoneBot 帮助
    """
    if args:
        matcher.set_arg("keyword", args)


@nonebot2.got("keyword", prompt="请输入搜索 Nonebot2 文档的关键字")
async def interactive_search_nonebot2_manual(matcher: Matcher, event: MessageEvent,
                                             keyword: str = ArgPlainText("keyword"),
                                             reject_times: int = Depends(save_nonebot_times)):
    """
    对话搜索 NoneBot 文档
    """
    await search_manual(keyword, "NoneBot2", reject_times, matcher, event.user_id)


@onebot_adapter.handle()
async def search_onebot_adapter_manual(matcher: Matcher, args: Message = CommandArg()):
    """
    搜索 OneBot 适配器 文档
    """
    if args:
        matcher.set_arg("keyword", args)


@onebot_adapter.got("keyword", prompt="请输入搜索 OneBot 适配器 文档的关键字")
async def interactive_search_onebot_adapter_manual(matcher: Matcher, event: MessageEvent,
                                                   keyword: str = ArgPlainText("keyword"),
                                                   reject_times: int = Depends(save_onebot_adapter_times)):
    """
    对话搜索 OneBot 适配器 文档
    """
    await search_manual(keyword, "OneBot 适配器", reject_times, matcher, event.user_id)


@page_command.handle()
async def get_page_info(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    user_id = event.user_id
    try:
        page = int(args.extract_plain_text())
    except ValueError:
        await matcher.finish(MessageSegment.text(f"不正确的页码：{args.extract_plain_text()}"), at_sender=True)
        return

    if search_result := user_pages.get(user_id):
        if page > (page_len := len(search_result)) or page <= 0:
            await matcher.finish(f"不存在的页码：{page}，当前页面总数：{page_len}", at_sender=True)
        next_page_number[user_id] = page + 1
        if last_use_plugins_list[user_id]:
            message = get_plugins_message(search_result[page - 1], page, page_len)
        else:
            message = get_message(search_result[page - 1], page, page_len)
        await matcher.finish(message)
    else:
        await matcher.finish("暂无缓存，请尝试搜索文档", at_sender=True)


@on_notice().handle()
async def next_page(matcher: Matcher, event: PokeNotifyEvent):
    user_id = event.user_id
    if page := next_page_number.get(user_id):
        if search_result := user_pages.get(user_id):
            if page > (page_len := len(search_result)):
                await matcher.finish(f"已到达最后一页，使用 /page <页码> 跳转到指定页", at_sender=True)
            next_page_number[user_id] += 1
            if last_use_plugins_list[user_id]:
                message = get_plugins_message(search_result[page - 1], page, page_len)
            else:
                message = get_message(search_result[page - 1], page, page_len)
            await matcher.finish(message)
        else:
            await matcher.finish("暂无缓存，请尝试搜索文档", at_sender=True)
    else:
        await matcher.finish("暂无缓存，请尝试搜索文档", at_sender=True)


@plugins_list.handle()
async def send_plugins_list(matcher: Matcher, event: MessageEvent):
    user_id = event.user_id
    if not index:
        await init_index()
    if not index:
        await matcher.finish("索引初始化失败，可能是网络问题", at_sender=True)
        return

    _plugins_list = index.get_plugins()
    save_pages(_plugins_list, user_id, plugin_config.rtfm_page)
    pages = user_pages[user_id]
    msg = get_plugins_message(pages[0], 1, len(pages))
    last_use_plugins_list[user_id] = True
    await matcher.finish(msg + "\n（使用 /page <页码> 查看指定页）")


@search_plugins.handle()
async def search_plugin_param_error(matcher: Matcher, args: ParserExit = ShellCommandArgs()):
    msg = Message()
    if args.status == 2:
        msg.append(f"错误的调用：\n\t{args.message}\n")
    msg.append(SEARCH_PLUGIN_HELP)
    await matcher.finish(msg)


@search_plugins.handle()
async def search_plugin_func(matcher: Matcher, event: MessageEvent, args: BaseNamespace = ShellCommandArgs()):
    args: Namespace
    user_id = event.user_id
    if not index:
        await init_index()
    if not index:
        await matcher.finish("索引初始化失败，可能是网络问题", at_sender=True)
        return

    _plugins_list = search_plugins_(
        keyword=args.keyword,
        no_tags=args.without_tag,
        no_name=args.without_name,
        no_author=args.without_author,
        no_desc=args.without_desc,
        percent=args.percent
    )
    if _plugins_list:
        save_pages(list(_plugins_list), user_id, plugin_config.rtfm_page)
        pages = user_pages[user_id]
        msg = get_plugins_message(pages[0], 1, len(pages))
        last_use_plugins_list[user_id] = True
        await matcher.finish(msg + "\n（使用 /page <页码> 查看指定页）")
    else:
        await matcher.finish(MessageSegment.text(f"未找到插件 {args.keyword}"), at_sender=True)
