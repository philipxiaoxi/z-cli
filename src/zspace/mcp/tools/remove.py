"""remove 工具 —— 删除 zspace NAS 上的文件或文件夹，支持个人空间和团队空间。"""

from ...api.file import delete_item
from ..base import McpTool


class RemoveTool(McpTool):
    name = "delete_item"
    description = "删除 zspace NAS 上的文件或文件夹，同时支持个人空间（/sata12/my/data）和团队空间（/sata12/public）路径"
    input_schema = {
        "type": "object",
        "properties": {
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要删除的文件/文件夹路径列表（移至回收站），支持个人空间和团队空间路径",
            },
            "show_hidden": {
                "type": "boolean",
                "description": "是否包含隐藏文件",
                "default": False,
            },
        },
        "required": ["paths"],
    }

    def handle(self, arguments: dict) -> str:
        return delete_item(
            paths=arguments["paths"],
            show_hidden=arguments.get("show_hidden", False),
        )
