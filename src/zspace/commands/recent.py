"""recent 命令 —— 获取最近访问的文件列表。"""

from ..api.file import list_recent_files
from .base import Command


class RecentCommand(Command):
    name = "recent"
    help = "获取最近访问的文件列表"

    def register(self, parser):
        parser.add_argument("--start", default="0", help="分页起始偏移")
        parser.add_argument("--num", default="100", help="每页条目数")
        parser.add_argument("--scope", default="1", choices=["1"], help="查询范围")
        parser.add_argument("--show-hidden", default="0", choices=["0", "1"], help="是否显示隐藏文件")

    def handle(self, args):
        print(list_recent_files(start=args.start, num=args.num, scope=args.scope, show_hidden=args.show_hidden))
