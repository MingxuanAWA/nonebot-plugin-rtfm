import pytest
from nonebug import App

MORE_RESULT = """搜索到以下结果：
1. 使用适配器--获得驱动器实例
https://v2.nonebot.dev/docs/tutorial/register-adapter#%E8%8E%B7%E5%BE%97%E9%A9%B1%E5%8A%A8%E5%99%A8%E5%AE%9E%E4%BE%8B
2. 安装驱动器--安装驱动器
https://v2.nonebot.dev/docs/start/install-driver
3. 选择驱动器--选择驱动器
https://v2.nonebot.dev/docs/tutorial/choose-driver"""


@pytest.mark.asyncio
async def test_adapter_onebot_search(app: App, init_plugin):
    from nonebot.adapters.onebot.v11 import Message
    from nonebot_plugin_rtfm import onebot_adapter as matcher
    from tests.utils import make_event, make_sender

    # simple
    async with app.test_matcher(matcher) as ctx:
        bot = ctx.create_bot()
        msg = Message("/rtfm 单元测试")
        event = make_event(message=msg, sender=make_sender())
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            Message(
                "搜索到以下结果：\n配置连接--反向 WebSocket 连接（推荐）\nhttps://onebot.adapters.nonebot.dev/docs/guide/setup/#%E5%8F%8D"
                "%E5%90%91-websocket-%E8%BF%9E%E6%8E%A5%E6%8E%A8%E8%8D%90"),
            None
        )

    # not found and reject
    async with app.test_matcher(matcher) as ctx:
        bot = ctx.create_bot()
        msg = Message("/obrtfm asdfghjkl")
        event = make_event(message=msg, sender=make_sender())
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            Message(
                "未在 {name} 文档找到 {keyword}，请输入其他关键字".format(
                    name="OneBot 适配器",
                    keyword="asdfghjkl"
                )),
            None
        )
        ctx.should_rejected()

        msg = Message("/rtfm get_bot")
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
        ctx.should_finished()

    # more result
    async with app.test_matcher(matcher) as ctx:
        bot = ctx.create_bot()
        msg = Message("/rtfm 驱动器")
        event = make_event(message=msg, sender=make_sender())
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, MORE_RESULT, None)
        ctx.should_finished()
