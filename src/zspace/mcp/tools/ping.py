"""check_connectivity 工具 —— AI 调用以检测与 zspace 的连通性。"""

from ...api.ping import ping
from ..base import McpTool


class PingTool(McpTool):
    name = "check_connectivity"
    description = "检查与 zspace NAS 本地代理的连通性（TCP + HTTP），适用于诊断连接问题"
    input_schema = {
        "type": "object",
        "properties": {
            "timeout": {
                "type": "integer",
                "description": "超时秒数，默认 5",
                "default": 5,
            },
        },
    }

    def handle(self, arguments: dict) -> str:
        return ping(timeout=arguments.get("timeout", 5))
