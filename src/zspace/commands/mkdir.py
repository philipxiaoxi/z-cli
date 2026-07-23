"""mkdir 命令 —— 在 NAS 上创建文件夹（支持个人空间和团队空间）。"""

from ..api.file import create_folder
from .base import Command


class MkdirCommand(Command):
    name = "mkdir"
    help = "在 NAS 上创建文件夹（支持个人空间和团队空间）"

    def register(self, parser):
        parser.add_argument("parent", help="父目录路径（个人空间如 /sata12/my/data，团队空间如 /sata12/public）")
        parser.add_argument("name", help="文件夹名称")
        parser.add_argument("--rename", default="0", choices=["0", "1"], help="冲突时是否自动重命名")

    def handle(self, args):
        print(create_folder(parent=args.parent, name=args.name, rename=args.rename))
