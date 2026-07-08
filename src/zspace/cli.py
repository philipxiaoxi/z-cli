import sys
import json
import argparse
import urllib.parse

import httpx

from .auth import build_headers, get_base_url


def _format_response(resp):
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text)
    sys.exit(0 if resp.is_success else 1)


def _cmd_list(args):
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
    parser = argparse.ArgumentParser(prog="zcli")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("mcp", help="Start MCP server")

    req = sub.add_parser("request", help="Send HTTP request")
    req.add_argument("method", choices=["get", "post", "put", "delete", "patch"])
    req.add_argument("url")
    req.add_argument("-d", "--data", help="Request body (JSON string)")
    req.add_argument("-H", "--header", action="append", help="Header (key:value)")

    ls = sub.add_parser("list", help="List files in a directory")
    ls.add_argument("path", help="Directory path (e.g. /sata12/my/data)")
    ls.add_argument("--start", default="0", help="Pagination start offset")
    ls.add_argument("--num", default="100", help="Number of items per page")
    ls.add_argument("--sortby", default="mtime_linux", help="Sort field")
    ls.add_argument("--order", default="desc", choices=["asc", "desc"], help="Sort order")
    ls.add_argument("--with-fields", default="encrypted,encrypt_icon,duration,nshare,ori,ext,height,weight,type,is_sys,dw,labels", help="Comma-separated fields to include")
    ls.add_argument("--show-hidden", default="0", choices=["0", "1"], help="Show hidden files")
    ls.add_argument("--dup", default="0", choices=["0", "1"], help="Include duplicates")

    args = parser.parse_args()

    if args.command == "mcp":
        from .mcp_server import serve
        serve()
        return

    if args.command == "list":
        _cmd_list(args)
        return

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
