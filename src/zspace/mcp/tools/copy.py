"""copy 工具 —— AI 调用以复制 NAS 上的文件或文件夹。"""

from ...api.file import copy_item
from ..base import McpTool


class CopyTool(McpTool):
    name = "copy_item"
    description = "复制zspace NAS 上的文件或文件夹"
    input_schema = {
        "type": "object",
        "properties": {
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要复制的文件/文件夹路径列表",
            },
            "to": {
                "type": "string",
                "description": "目标路径",
            },
            "rename": {
                "type": "string",
                "description": "冲突时是否自动重命名（0/1），默认为 0",
                "default": "0",
            },
        },
        "required": ["paths", "to"],
    }

    def handle(self, arguments: dict) -> str:
        paths = arguments["paths"]
        to = arguments["to"]
        rename = arguments.get("rename", "0")
        return copy_item(paths=paths, to=to, rename=rename)
