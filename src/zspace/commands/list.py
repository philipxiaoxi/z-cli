"""list 命令 —— 列出目录中的文件（支持个人空间和团队空间）。"""

import sys

from ..api.file import list_files, list_team_files
from .base import Command


class ListCommand(Command):
    name = "list"
    help = "列出目录中的文件（支持个人空间和团队空间）"

    def register(self, parser):
        parser.add_argument("path", nargs="?", help=(
            "目录路径（个人空间如 /sata12/my/data，"
            "团队空间如 /sata12/public；--team 下默认 /public）"
        ))
        parser.add_argument("--team", action="store_true", help="列出团队空间（公共空间）目录")
        parser.add_argument("--start", default="0", help="分页起始偏移")
        parser.add_argument("--num", default="100", help="每页条目数")
        parser.add_argument("--sortby", default="mtime_linux", help="排序字段（仅个人空间）")
        parser.add_argument("--order", default="desc", choices=["asc", "desc"], help="排序方向（仅个人空间）")
        parser.add_argument(
            "--with-fields",
            default=(
                "encrypted,encrypt_icon,duration,nshare,ori,"
                "ext,height,weight,type,is_sys,dw,labels"
            ),
            help="返回的额外字段，逗号分隔（仅个人空间）",
        )
        parser.add_argument("--show-hidden", default="0", choices=["0", "1"], help="是否显示隐藏文件（仅个人空间）")
        parser.add_argument("--dup", default="0", choices=["0", "1"], help="是否包含重复文件（仅个人空间）")

    def handle(self, args):
        if args.team:
            print(list_team_files(
                path=args.path or "/public",
                start=args.start,
                num=args.num,
            ))
        else:
            if not args.path:
                print("错误：个人空间模式下必须指定 path", file=sys.stderr)
                sys.exit(1)
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
