from typing import Set, List

from nonebot import on_command, get_driver, on_notice
from nonebot.adapters.onebot.v11 import Message, Event, MessageEvent, MessageSegment, PokeNotifyEvent
from nonebot.internal.matcher import Matcher
from nonebot.internal.params import ArgPlainText, Depends
from nonebot.params import CommandArg

from .algolia import search, SearchResult
from .config import Config

# API Key
NONEBOT2_APP_ID = "X0X5UACHZQ"
NONEBOT2_API_KEY = "ac03e1ac2bd0812e2ea38c0cc1ea38c5"
ONEBOT_ADAPTER_APP_ID = "UXS5VZ9AQX"
ONEBOT_ADAPTER_API_KEY = "f1e9e8357ce05e81665c586c978a7661"

# matcher
nonebot2 = on_command("rtfm")
nonebot2.__help_name__ = "rtfm"
nonebot2.__help_info__ = "搜索 NoneBot2 文档"
onebot_adapter = on_command("obrtfm")
nonebot2.__help_name__ = "obrtfm"
nonebot2.__help_info__ = "搜索 OneBot 适配器 文档"
page_command = on_command("page")
page_command.__help_name__ = "page"
page_command.__help_info__ = "查看缓存的指定页码的文档"

# session and config
plugin_config = Config.parse_obj(get_driver().config)
user_times = {"nonebot2": {}, "onebot_adapter": {}}
next_page_number = dict()
user_pages = dict()

# nonebot-plugin-help
__help_version__ = "0.1.0"
__help_plugin_name__ = "NoneBot2 文档搜索"
__usage__ = """NoneBot2 文档搜索
命令：
/rtfm [关键字]      搜索 NoneBot2 文档，未输入关键字进入对话模式
/obrtfm [关键字]    搜索 OneBot 适配器 文档，未输入关键字进入对话模式
/page <页码>        查看缓存的指定页码的文档
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


def save_pages(page: Set[SearchResult], user_id: int, count: int):
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
    user_times["nonebot2"][user_id] = (user_times.get("nonebot2", None)).get(user_id, 0) + 1
    if user_times["nonebot2"][user_id] >= 3:
        user_times["nonebot2"][user_id] = 0
        return 0
    return user_times["nonebot2"][user_id]


def save_onebot_adapter_times(event: Event):
    user_id = event.get_user_id()
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
        await matcher.finish(get_message(search_result[page - 1], page, page_len))
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
            await matcher.finish(get_message(search_result[page - 1], page, page_len))
        else:
            await matcher.finish("暂无缓存，请尝试搜索文档", at_sender=True)
    else:
        await matcher.finish("暂无缓存，请尝试搜索文档", at_sender=True)
