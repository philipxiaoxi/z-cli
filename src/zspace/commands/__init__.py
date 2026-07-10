"""命令注册中心 —— CLI 入口 + 所有子命令注册，自动接入 argparse。"""

import argparse
import sys

from ..api import ApiError
from .base import Command
from .copy import CopyCommand
from .create import CreateCommand
from .list import ListCommand
from .mcp import McpCommand
from .mkdir import MkdirCommand
from .move import MoveCommand
from .ping import PingCommand
from .pool import PoolCommand
from .poolname import PoolnameCommand
from .read import ReadCommand
from .recent import RecentCommand
from .remove import RemoveCommand
from .rename import RenameCommand
from .search import SearchCommand
from .skills import SkillsCommand

# 注册表：新增命令只需在此处添加类引用
_BUILTINS: list[type[Command]] = [
    CopyCommand,
    CreateCommand,
    ListCommand,
    McpCommand,
    MkdirCommand,
    MoveCommand,
    PingCommand,
    PoolnameCommand,
    PoolCommand,
    ReadCommand,
    RecentCommand,
    RemoveCommand,
    RenameCommand,
    SearchCommand,
    SkillsCommand,
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


def main():
    """CLI 入口 —— 解析参数并路由到对应子命令。"""
    parser = argparse.ArgumentParser(
        prog="zcli",
        description="zspace 私有云命令行工具",
    )
    register_all(parser.add_subparsers(dest="command", required=True))
    args = parser.parse_args()

    try:
        args._handler(args)
    except ApiError as e:
        print(f"错误 [{e.code}]: {e.msg}", file=sys.stderr)
        sys.exit(1)
