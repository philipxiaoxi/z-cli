"""MCP 工具注册中心 —— 所有工具在此注册后自动接入 MCP 服务器。"""

from __future__ import annotations

from ..base import McpTool
from .copy import CopyTool
from .create import CreateFileTool
from .list import ListFilesTool
from .mkdir import MkdirTool
from .move import MoveTool
from .ping import PingTool
from .pool import PoolTool
from .poolname import PoolnameTool
from .read import ReadFileTool
from .recent import ListRecentFilesTool
from .remove import RemoveTool
from .rename import RenameTool
from .search import SearchTool
from .teamlist import ListTeamFilesTool

# 工具注册表：新增工具只需在此处添加类引用
_BUILTINS: list[type[McpTool]] = [
    CopyTool,
    CreateFileTool,
    ListFilesTool,
    MkdirTool,
    MoveTool,
    PingTool,
    PoolTool,
    PoolnameTool,
    ReadFileTool,
    ListRecentFilesTool,
    RemoveTool,
    RenameTool,
    SearchTool,
    ListTeamFilesTool,
]


def get_all_tools() -> list[McpTool]:
    """返回所有已注册的工具实例列表。"""
    return [cls() for cls in _BUILTINS]
