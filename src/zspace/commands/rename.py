"""rename 命令 —— 重命名 NAS 上的文件或文件夹（支持个人空间和团队空间）。"""

from ..api.file import rename_item
from .base import Command


class RenameCommand(Command):
    name = "rename"
    help = "重命名 NAS 上的文件或文件夹（支持个人空间和团队空间）"

    def register(self, parser):
        parser.add_argument("path", help=(
            "文件/文件夹的完整路径"
            "（个人空间如 /sata12/my/data/旧名称，团队空间如 /sata12/public/旧名称）"
        ))
        parser.add_argument("newname", help="新名称（仅名称，不包含路径）")

    def handle(self, args):
        print(rename_item(path=args.path, newname=args.newname))
