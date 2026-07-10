"""ping 命令 —— 检查与 zspace 本地代理的连通性。"""

from ..api.ping import ping
from .base import Command


class PingCommand(Command):
    name = "ping"
    help = "检查与 zspace 本地代理的连通性"

    def register(self, parser):
        parser.add_argument("--timeout", type=int, default=5, help="超时秒数，默认 5")

    def handle(self, args):
        print(ping(timeout=args.timeout))
