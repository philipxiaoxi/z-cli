"""remove 命令 —— 删除 NAS 上的文件或文件夹（支持个人空间和团队空间）。"""

from ..api.file import delete_item
from .base import Command


class RemoveCommand(Command):
    name = "remove"
    help = "删除 NAS 上的文件或文件夹（支持个人空间和团队空间）"

    def register(self, parser):
        parser.add_argument("paths", help=(
            "要删除的文件/文件夹路径，多个路径用逗号分隔"
            "（个人空间如 /sata12/my/data，团队空间如 /sata12/public）"
        ))
        parser.add_argument("--show-hidden", action="store_true", help="是否包含隐藏文件")

    def handle(self, args):
        paths = [p.strip() for p in args.paths.split(",")]
        print(delete_item(paths=paths if len(paths) > 1 else paths[0], show_hidden=args.show_hidden))
