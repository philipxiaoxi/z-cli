"""poolname 工具 —— AI 调用以查看存储池名称映射。"""

from ...api.user import get_pool_names
from ..base import McpTool


class PoolnameTool(McpTool):
    name = "get_pool_names"
    description = "获取存储池名称映射（pool key \u2192 display name）"
    input_schema = {
        "type": "object",
        "properties": {},
    }

    def handle(self, arguments: dict) -> str:
        return get_pool_names()
