"""read 命令 —— 读取 NAS 上文本文件内容（支持个人空间和团队空间）。"""

from ..api.file import read_file
from .base import Command


class ReadCommand(Command):
    name = "read"
    help = "读取 NAS 上文本文件的内容（支持个人空间和团队空间）"

    def register(self, parser):
        parser.add_argument("path", help=(
            "文件完整路径（个人空间如 /sata12/my/data/a.txt，"
            "团队空间如 /sata12/public/a.txt）"
        ))
        parser.add_argument("--remote-port", default="8050", help="NAS web 服务端口，默认 8050")

    def handle(self, args):
        print(read_file(path=args.path, remote_port=args.remote_port))
