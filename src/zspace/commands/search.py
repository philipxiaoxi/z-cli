"""search 命令 —— 搜索 NAS 上的文件（支持个人空间和团队空间）。"""

from ..api.file import search_files
from .base import Command


class SearchCommand(Command):
    name = "search"
    help = "搜索 NAS 上的文件（支持个人空间和团队空间）"

    def register(self, parser):
        parser.add_argument("name", help="搜索关键词")
        parser.add_argument("--path", default="/sata12/my/data", help=(
            "搜索范围路径（个人空间默认，团队空间传 /sata12/public）"
        ))
        parser.add_argument("--order-by", default="0", choices=["0", "1", "2"],
                            help="排序方式 (0=名称, 1=修改时间, 2=大小)")
        parser.add_argument("--ftype", default="", help="文件类型筛选")
        parser.add_argument("--is-dir", default="", choices=["", "0", "1"],
                            help="是否仅目录")
        parser.add_argument("--min-size", default="0", help="最小文件大小（字节）")
        parser.add_argument("--max-size", default="0", help="最大文件大小（字节）")
        parser.add_argument("--start", default="0", help="分页起始偏移")
        parser.add_argument("--num", default="30", help="每页条目数")
        parser.add_argument("--shared-only", default="0", choices=["0", "1"],
                            help="仅搜索共享文件")
        parser.add_argument("--show-hidden", default="0", choices=["0", "1"],
                            help="是否显示隐藏文件")

    def handle(self, args):
        print(search_files(
            name=args.name,
            file_path=args.path,
            order_by=args.order_by,
            ftype=args.ftype,
            is_dir=args.is_dir,
            min_size=args.min_size,
            max_size=args.max_size,
            start=args.start,
            num=args.num,
            shared_only=args.shared_only,
            show_hidden=args.show_hidden,
        ))
