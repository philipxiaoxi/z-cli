"""mcp 命令 —— 启动 MCP 服务器。"""

from .base import Command


class McpCommand(Command):
    name = "mcp"
    help = "启动 MCP 服务器"

    def register(self, parser):
        pass

    def handle(self, args):
        from ..mcp_server import serve
        serve()
