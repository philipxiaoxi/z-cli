"""move 命令 —— 移动或重命名 NAS 上的文件或文件夹。"""

from ..api.file import move_item
from .base import Command


class MoveCommand(Command):
    name = "move"
    help = "移动或重命名 NAS 上的文件或文件夹"

    def register(self, parser):
        parser.add_argument("paths", help="要移动的源路径，多个路径用逗号分隔")
        parser.add_argument("to", help="目标路径")
        parser.add_argument("--rename", default="0", choices=["0", "1"], help="冲突时是否自动重命名")

    def handle(self, args):
        paths = [p.strip() for p in args.paths.split(",")]
        print(move_item(paths=paths if len(paths) > 1 else paths[0], to=args.to, rename=args.rename))
