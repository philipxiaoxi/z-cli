"""create 命令 —— 在 NAS 上创建文件（支持个人空间和团队空间）。"""

from ..api.file import create_file
from .base import Command


class CreateCommand(Command):
    name = "create"
    help = "在 NAS 上创建文件（支持个人空间和团队空间）"

    def register(self, parser):
        parser.add_argument("path", help="文件完整路径（个人空间如 /sata12/my/data/a.txt，团队空间如 /sata12/public/a.txt）")
        parser.add_argument("--rename", default="0", choices=["0", "1"], help="冲突时是否自动重命名")
        parser.add_argument("--content", default="", help="文件内容文本")

    def handle(self, args):
        content = args.content.encode("utf-8") if args.content else b""
        print(create_file(path=args.path, rename=args.rename, content=content))
