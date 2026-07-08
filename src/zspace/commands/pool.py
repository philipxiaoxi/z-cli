"""pool 命令 —— 查看存储池信息。"""

from ..api.pool import get_pool_info
from .base import Command


class PoolCommand(Command):
    name = "pool"
    help = "查看存储池信息"

    def register(self, parser):
        pass

    def handle(self, args):
        print(get_pool_info())
