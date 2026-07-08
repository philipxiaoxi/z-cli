"""request 命令 —— 发送自定义 HTTP 请求。"""

import json

import httpx

from .base import Command, format_response


class RequestCommand(Command):
    name = "request"
    help = "发送自定义 HTTP 请求"

    def register(self, parser):
        parser.add_argument("method", choices=["get", "post", "put", "delete", "patch"])
        parser.add_argument("url")
        parser.add_argument("-d", "--data", help="JSON 格式的请求体")
        parser.add_argument("-H", "--header", action="append", help="请求头，格式 key:value（可重复）")

    def handle(self, args):
        headers = {}
        for h in args.header or []:
            key, _, val = h.partition(":")
            headers[key.strip()] = val.strip()

        data = None
        if args.data:
            data = json.loads(args.data)

        resp = httpx.request(args.method, args.url, headers=headers, json=data)
        format_response(resp)
