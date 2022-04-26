import pytest
from nonebug import App

MORE_RESULTS = """搜索到以下结果：
1. 使用适配器--使用适配器
https://v2.nonebot.dev/docs/tutorial/register-adapter
2. 商店--商店
适配器
https://v2.nonebot.dev/store
3. 安装协议适配器--安装协议适配器
https://v2.nonebot.dev/docs/start/install-adapter"""


@pytest.mark.asyncio
async def test_nonebot2_search(app: App, init_plugin):
    from nonebot.adapters.onebot.v11 import Message
    from nonebot_plugin_rtfm import nonebot2 as matcher
    from tests.utils import make_event, make_sender

    # simple
    async with app.test_matcher(matcher) as ctx:
        bot = ctx.create_bot()
        msg = Message("/rtfm 单元测试")
        event = make_event(message=msg, sender=make_sender())
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            Message("搜索到以下结果：\n单元测试--单元测试\nhttps://v2.nonebot.dev/docs/advanced/unittest"),
            None
        )

    # not found and reject
    async with app.test_matcher(matcher) as ctx:
        bot = ctx.create_bot()
        msg = Message("/rtfm asdfghjkl")
        event = make_event(message=msg, sender=make_sender())
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            Message("未在 NoneBot2 文档找到 asdfghjkl，请输入其他关键字"),
            None
        )
        ctx.should_rejected()

        msg = Message("get_bot")
        event = make_event(message=msg, sender=make_sender())
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            Message("搜索到以下结果：\nnonebot--函数 get_bot(self_id=None)\nhttps://v2.nonebot.dev/docs/api/index#get_bot"),
            None
        )
        ctx.should_finished()

    # many rejecting times
    async with app.test_matcher(matcher) as ctx:
        bot = ctx.create_bot()
        msg = Message("/rtfm asdfghjkl")
        event = make_event(message=msg, sender=make_sender())
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            Message(
                "未在 {name} 文档找到 {keyword}，请输入其他关键字".format(
                    name="NoneBot2",
                    keyword="asdfghjkl"
                )),
            None
        )
        ctx.should_rejected()

        msg = Message("asdfghjkl")
        event = make_event(message=msg, sender=make_sender())
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            Message(
                "未在 {name} 文档找到 {keyword}，请输入其他关键字".format(
                    name="NoneBot2",
                    keyword="asdfghjkl"
                )),
            None
        )
        ctx.should_rejected()
        ctx.receive_event(bot, event)
        ctx.should_finished()

    # more results
    async with app.test_matcher(matcher) as ctx:
        bot = ctx.create_bot()
        msg = Message("/rtfm 适配器")
        event = make_event(message=msg, sender=make_sender())
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, Message(MORE_RESULTS), None)
        ctx.should_finished()
