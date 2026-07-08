"""copy 命令 —— 复制 NAS 上的文件或文件夹。"""

from ..api.file import copy_item
from .base import Command


class CopyCommand(Command):
    name = "copy"
    help = "复制 NAS 上的文件或文件夹"

    def register(self, parser):
        parser.add_argument("paths", help="要复制的源路径，多个路径用逗号分隔")
        parser.add_argument("to", help="目标路径")
        parser.add_argument("--rename", default="0", choices=["0", "1"], help="冲突时是否自动重命名")

    def handle(self, args):
        paths = [p.strip() for p in args.paths.split(",")]
        print(copy_item(paths=paths if len(paths) > 1 else paths[0], to=args.to, rename=args.rename))
