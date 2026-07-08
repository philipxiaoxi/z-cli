"""poolname 命令 —— 查看存储池名称映射。"""

from ..api.user import get_pool_names
from .base import Command


class PoolnameCommand(Command):
    name = "poolname"
    help = "查看存储池名称映射（pool key \u2192 display name）"

    def register(self, parser):
        pass

    def handle(self, args):
        print(get_pool_names())
