"""MCP 工具注册中心 —— 所有工具在此注册后自动接入 MCP 服务器。"""

from ..base import McpTool
from .list import ListFilesTool
from .request import RequestTool

# 工具注册表：新增工具只需在此处添加类引用
_BUILTINS: list[type[McpTool]] = [
    ListFilesTool,
    RequestTool,
]


def get_all_tools() -> list[McpTool]:
    """返回所有已注册的工具实例列表。"""
    return [cls() for cls in _BUILTINS]
