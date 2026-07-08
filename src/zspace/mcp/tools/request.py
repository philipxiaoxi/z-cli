"""request 工具 —— AI 调用以发送自定义 HTTP 请求。"""

import json

import httpx

from ...client import request
from ..base import McpTool


class RequestTool(McpTool):
    name = "make_request"
    description = "向任意 URL 发送 HTTP 请求"
    input_schema = {
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                "description": "HTTP 请求方法",
            },
            "url": {"type": "string", "description": "目标 URL"},
            "headers": {
                "type": "object",
                "description": "可选的 HTTP 请求头 (key: value)",
                "additionalProperties": {"type": "string"},
            },
            "body": {
                "type": "object",
                "description": "可选的 JSON 请求体",
            },
        },
        "required": ["method", "url"],
    }

    def handle(self, arguments: dict) -> str:
        resp = request(
            method=arguments["method"],
            url=arguments["url"],
            headers=arguments.get("headers"),
            json=arguments.get("body"),
        )
        try:
            data = resp.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            return resp.text
