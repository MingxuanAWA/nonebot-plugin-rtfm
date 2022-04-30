from argparse import Namespace as BaseNamespace

from nonebot.rule import ArgumentParser


class Namespace(BaseNamespace):
    keyword: str
    percent: float
    without_tag: bool
    without_name: bool
    without_author: bool
    without_desc: bool


parser = ArgumentParser("搜索插件")

parser.add_argument("keyword", help="查询关键字", action="store", type=str)
parser.add_argument("-t", "--without_tag", help="查询时不使用标签查询", action="store_true")
parser.add_argument("-n", "--without_name", help="查询时不使用插件名称查询", action="store_true")
parser.add_argument("-a", "--without_author", help="查询时不使用作者名查询", action="store_true")
parser.add_argument("-d", "--without_desc", help="查询时不使用描述查询", action="store_true")
parser.add_argument("-p", "--percent", help="相似度，越接近1相似度越高", action="store", type=float)
