"""list 命令 —— 列出 NAS 目录中的文件。"""

from ..api.file import list_files
from .base import Command


class ListCommand(Command):
    name = "list"
    help = "列出 NAS 目录中的文件"

    def register(self, parser):
        parser.add_argument("path", help="目录路径（如 /sata12/my/data）")
        parser.add_argument("--start", default="0", help="分页起始偏移")
        parser.add_argument("--num", default="100", help="每页条目数")
        parser.add_argument("--sortby", default="mtime_linux", help="排序字段")
        parser.add_argument("--order", default="desc", choices=["asc", "desc"], help="排序方向")
        parser.add_argument(
            "--with-fields",
            default=(
                "encrypted,encrypt_icon,duration,nshare,ori,"
                "ext,height,weight,type,is_sys,dw,labels"
            ),
            help="返回的额外字段（逗号分隔）",
        )
        parser.add_argument("--show-hidden", default="0", choices=["0", "1"], help="是否显示隐藏文件")
        parser.add_argument("--dup", default="0", choices=["0", "1"], help="是否包含重复文件")

    def handle(self, args):
        print(list_files(
            path=args.path,
            start=args.start,
            num=args.num,
            sortby=args.sortby,
            order=args.order,
            with_fields=args.with_fields,
            show_hidden=args.show_hidden,
            dup=args.dup,
        ))
