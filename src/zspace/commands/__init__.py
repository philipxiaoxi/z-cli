"""命令注册中心 —— 所有子命令在此注册后自动接入 CLI。"""

from .base import Command
from .list import ListCommand
from .mcp import McpCommand
from .mkdir import MkdirCommand
from .pool import PoolCommand
from .request import RequestCommand

# 注册表：新增命令只需在此处添加类引用
_BUILTINS: list[type[Command]] = [
    ListCommand,
    McpCommand,
    MkdirCommand,
    PoolCommand,
    RequestCommand,
]


def register_all(subparsers):
    """将所有已注册的命令绑定到 argparse SubParsers。

    Args:
        subparsers: argparse.add_subparsers() 返回的对象。
    """
    for cls in _BUILTINS:
        cmd = cls()
        p = subparsers.add_parser(cmd.name, help=cmd.help)
        cmd.register(p)
        p.set_defaults(_handler=cmd.handle)
