"""mkdir 工具 —— AI 调用以在 NAS 上创建文件夹。"""

from ...api.file import create_folder
from ..base import McpTool


class MkdirTool(McpTool):
    name = "create_folder"
    description = "在zspace NAS 上创建新文件夹"
    input_schema = {
        "type": "object",
        "properties": {
            "parent": {
                "type": "string",
                "description": "父目录路径，如 /sata12/my/data",
            },
            "name": {
                "type": "string",
                "description": "要创建的文件夹名称",
            },
            "rename": {
                "type": "string",
                "enum": ["0", "1"],
                "description": "冲突时是否自动重命名，默认 0",
                "default": "0",
            },
        },
        "required": ["parent", "name"],
    }

    def handle(self, arguments: dict) -> str:
        return create_folder(
            parent=arguments["parent"],
            name=arguments["name"],
            rename=arguments.get("rename", "0"),
        )
