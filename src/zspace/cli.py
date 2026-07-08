"""命令行入口 —— 基于 argparse 实现 zcli 命令。

支持子命令:
  - mcp:     启动 MCP 服务器
  - request: 发送自定义 HTTP 请求
  - list:    列出 NAS 目录中的文件
"""

import sys
import json
import argparse
import urllib.parse

import httpx

from .auth import build_headers, get_base_url


def _format_response(resp: httpx.Response):
    """格式化输出 HTTP 响应。

    优先尝试 JSON 格式化输出，失败则输出原始文本。
    以非零状态码退出表示请求失败。
    """
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text)
    sys.exit(0 if resp.is_success else 1)


def _cmd_list(args):
    """处理 list 子命令：向zspace API 请求文件列表。

    从 auth 模块获取认证凭据和请求头，
    以 application/x-www-form-urlencoded 格式 POST 到文件列表接口。
    """
    data = {
        "start": args.start,
        "num": args.num,
        "sortby": args.sortby,
        "order": args.order,
        "path": args.path,
        "with_fields": args.with_fields,
        "show_hidden": args.show_hidden,
        "dup": args.dup,
    }
    resp = httpx.request(
        "POST",
        f"{get_base_url()}/v2/file/list/stream",
        headers=build_headers(args.path),
        content=urllib.parse.urlencode(data),
    )
    _format_response(resp)


def main():
    """主入口：解析命令行参数并分发到对应子命令处理器。"""
    parser = argparse.ArgumentParser(
        prog="zcli",
        description="zspace私有云命令行工具",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # mcp 子命令：启动 MCP 服务器
    sub.add_parser("mcp", help="启动 MCP 服务器")

    # request 子命令：发送自定义 HTTP 请求
    req = sub.add_parser("request", help="发送自定义 HTTP 请求")
    req.add_argument("method", choices=["get", "post", "put", "delete", "patch"])
    req.add_argument("url")
    req.add_argument("-d", "--data", help="JSON 格式的请求体")
    req.add_argument("-H", "--header", action="append", help="请求头，格式 key:value（可重复）")

    # list 子命令：列出 NAS 文件
    ls = sub.add_parser("list", help="列出 NAS 目录中的文件")
    ls.add_argument("path", help="目录路径（如 /sata12/my/data）")
    ls.add_argument("--start", default="0", help="分页起始偏移")
    ls.add_argument("--num", default="100", help="每页条目数")
    ls.add_argument("--sortby", default="mtime_linux", help="排序字段")
    ls.add_argument("--order", default="desc", choices=["asc", "desc"], help="排序方向")
    ls.add_argument(
        "--with-fields",
        default=(
            "encrypted,encrypt_icon,duration,nshare,ori,"
            "ext,height,weight,type,is_sys,dw,labels"
        ),
        help="返回的额外字段（逗号分隔）",
    )
    ls.add_argument("--show-hidden", default="0", choices=["0", "1"], help="是否显示隐藏文件")
    ls.add_argument("--dup", default="0", choices=["0", "1"], help="是否包含重复文件")

    args = parser.parse_args()

    # 分发子命令
    if args.command == "mcp":
        from .mcp_server import serve
        serve()
        return

    if args.command == "list":
        _cmd_list(args)
        return

    # request 子命令处理
    headers = {}
    for h in args.header or []:
        key, _, val = h.partition(":")
        headers[key.strip()] = val.strip()

    data = None
    if args.data:
        data = json.loads(args.data)

    resp = httpx.request(args.method, args.url, headers=headers, json=data)
    _format_response(resp)


if __name__ == "__main__":
    main()
