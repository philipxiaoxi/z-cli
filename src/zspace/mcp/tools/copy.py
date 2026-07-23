"""copy 工具 —— AI 调用以复制 NAS 上的文件或文件夹，支持个人空间和团队空间。"""

from ...api.file import copy_item
from ..base import McpTool


class CopyTool(McpTool):
    name = "copy_item"
    description = "复制 zspace NAS 上的文件或文件夹，同时支持个人空间（/sata12/my/data）和团队空间（/sata12/public）路径"
    input_schema = {
        "type": "object",
        "properties": {
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要复制的文件/文件夹路径列表，支持个人空间和团队空间路径",
            },
            "to": {
                "type": "string",
                "description": "目标路径，支持个人空间和团队空间路径",
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
