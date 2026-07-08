import sys
import json
import argparse

from .client import request


def main():
    parser = argparse.ArgumentParser(prog="zcli")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("mcp", help="Start MCP server")

    req = sub.add_parser("request", help="Send HTTP request")
    req.add_argument("method", choices=["get", "post", "put", "delete", "patch"])
    req.add_argument("url")
    req.add_argument("-d", "--data", help="Request body (JSON string)")
    req.add_argument("-H", "--header", action="append", help="Header (key:value)")

    args = parser.parse_args()

    if args.command == "mcp":
        from .mcp_server import serve
        serve()
        return

    headers = {}
    for h in args.header or []:
        key, _, val = h.partition(":")
        headers[key.strip()] = val.strip()

    data = None
    if args.data:
        data = json.loads(args.data)

    resp = request(args.method, args.url, headers=headers, json=data)

    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text)

    sys.exit(0 if resp.is_success else 1)


if __name__ == "__main__":
    main()
