"""teamlist 命令 —— 列出团队空间（公共空间）目录中的文件。"""

from ..api.file import list_team_files
from .base import Command


class TeamListCommand(Command):
    name = "teamlist"
    help = "列出团队空间（公共空间）目录中的文件"

    def register(self, parser):
        parser.add_argument("path", nargs="?", default="/public", help="团队空间目录路径（默认 /public）")
        parser.add_argument("--start", default="0", help="分页起始偏移")
        parser.add_argument("--num", default="100", help="每页条目数")

    def handle(self, args):
        print(list_team_files(path=args.path, start=args.start, num=args.num))
