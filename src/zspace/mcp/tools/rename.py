"""rename 工具 —— AI 调用以重命名 NAS 上的文件或文件夹，支持个人空间和团队空间。"""

from ...api.file import rename_item
from ..base import McpTool


class RenameTool(McpTool):
    name = "rename_item"
    description = "重命名 zspace NAS 上的文件或文件夹，同时支持个人空间（/sata12/my/data）和团队空间（/sata12/public）路径"
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件/文件夹的完整路径，如 /sata12/my/data/旧名称，支持个人空间和团队空间",
            },
            "newname": {
                "type": "string",
                "description": "新名称（仅名称，不包含路径）",
            },
        },
        "required": ["path", "newname"],
    }

    def handle(self, arguments: dict) -> str:
        return rename_item(
            path=arguments["path"],
            newname=arguments["newname"],
        )
