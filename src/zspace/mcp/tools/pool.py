"""pool 工具 —— AI 调用以查看存储池信息。"""

from ...api.pool import get_pool_info
from ..base import McpTool


class PoolTool(McpTool):
    name = "get_pool_info"
    description = "查看zspace NAS 存储池信息"
    input_schema = {
        "type": "object",
        "properties": {},
    }

    def handle(self, arguments: dict) -> str:
        return get_pool_info()
