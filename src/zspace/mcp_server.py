"""MCP (Model Context Protocol) 服务器。

提供 make_request 工具，供 AI 助手（如 Claude）调用，
实现对zspace NAS 的 HTTP 操作。
"""

import asyncio
import json

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import Server

from .client import request

server = Server("zspace")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """注册 MCP 工具列表。"""
    return [
        types.Tool(
            name="make_request",
            description="向任意 URL 发送 HTTP 请求",
            inputSchema={
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
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """处理 MCP 工具调用。

    Args:
        name: 工具名称。
        arguments: 工具参数。

    Returns:
        list[types.TextContent]: 响应文本列表。
    """
    if name != "make_request":
        raise ValueError(f"未知工具: {name}")

    resp = request(
        method=arguments["method"],
        url=arguments["url"],
        headers=arguments.get("headers"),
        json=arguments.get("body"),
    )

    try:
        data = resp.json()
        text = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        text = resp.text

    return [types.TextContent(type="text", text=text)]


def serve():
    """启动 MCP 服务器（同步入口）。"""
    asyncio.run(_run())


async def _run():
    """通过 stdio 启动 MCP 服务器事件循环。"""
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())
