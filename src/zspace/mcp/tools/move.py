"""move 工具 —— AI 调用以移动或重命名 NAS 上的文件或文件夹。"""

from ...api.file import move_item
from ..base import McpTool


class MoveTool(McpTool):
    name = "move_item"
    description = "移动或重命名zspace NAS 上的文件或文件夹"
    input_schema = {
        "type": "object",
        "properties": {
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要移动的文件/文件夹路径列表",
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
        return move_item(paths=paths, to=to, rename=rename)
