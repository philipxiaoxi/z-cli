"""read_file 工具 —— AI 调用以读取 NAS 上文本文件内容，支持个人空间和团队空间。"""

from ...api.file import read_file
from ..base import McpTool


class ReadFileTool(McpTool):
    name = "read_file"
    description = "读取 zspace NAS 上文本文件的内容（仅限文本文件，非文本文件返回错误），同时支持个人空间（/sata12/my/data）和团队空间（/sata12/public）路径"
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "文件完整路径，支持个人空间和团队空间路径",
            },
        },
        "required": ["path"],
    }

    def handle(self, arguments: dict) -> str:
        return read_file(path=arguments["path"])
