"""create 工具 —— AI 调用以在 NAS 上创建文件。"""

from ...api.file import create_file
from ..base import McpTool


class CreateFileTool(McpTool):
    name = "create_file"
    description = "在zspace NAS 上创建文件"
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件完整路径",
            },
            "rename": {
                "type": "string",
                "description": "冲突时是否自动重命名（0/1），默认为 0",
                "default": "0",
            },
            "content": {
                "type": "string",
                "description": "文件内容文本（可选）",
                "default": "",
            },
        },
        "required": ["path"],
    }

    def handle(self, arguments: dict) -> str:
        path = arguments["path"]
        rename = arguments.get("rename", "0")
        content = arguments.get("content", "")
        content_bytes = content.encode("utf-8") if content else b""
        return create_file(path=path, rename=rename, content=content_bytes)
