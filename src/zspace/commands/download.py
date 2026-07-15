"""download 命令 —— 下载 NAS 上的文件。"""

from pathlib import Path

from ..api.file import download_file
from .base import Command


class DownloadCommand(Command):
    name = "download"
    help = "下载 NAS 上的文件"

    def register(self, parser):
        parser.add_argument("path", help="NAS 文件完整路径")
        parser.add_argument("output_dir", help="本地保存目录")

    def handle(self, args):
        data = download_file(path=args.path)
        dest = Path(args.output_dir) / args.path.rsplit("/", 1)[-1]
        dest.write_bytes(data)
        print(f"已下载到 {dest}")
