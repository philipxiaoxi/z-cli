"""MCP 服务器 —— 通过 stdio 与 AI 助手通信。

基于 MCP SDK，将从 tools/ 注册的所有工具暴露给 AI 调用。
"""

import asyncio

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import Server

from .tools import get_all_tools

server = Server("zspace")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """注册 MCP 工具列表 —— 自动收集 tools/ 下所有工具。"""
    return [tool.to_mcp_tool() for tool in get_all_tools()]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """处理 MCP 工具调用 —— 按名称路由到对应工具的 handle 方法。"""
    for tool in get_all_tools():
        if tool.name == name:
            text = tool.handle(arguments)
            return [types.TextContent(type="text", text=text)]
    raise ValueError(f"未知工具: {name}")


def serve():
    """启动 MCP 服务器（同步入口）。"""
    asyncio.run(_run())


async def _run():
    """通过 stdio 启动 MCP 服务器事件循环。"""
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())
