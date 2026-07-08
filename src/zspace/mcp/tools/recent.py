"""recent 工具 —— AI 调用以获取最近访问的文件列表。"""

from ...api.file import list_recent_files
from ..base import McpTool


class ListRecentFilesTool(McpTool):
    name = "list_recent_files"
    description = "获取 zspace NAS 上最近访问的文件列表"
    input_schema = {
        "type": "object",
        "properties": {
            "start": {
                "type": "string",
                "description": "分页起始偏移，默认为 0",
                "default": "0",
            },
            "num": {
                "type": "string",
                "description": "每页条目数，默认为 100",
                "default": "100",
            },
            "scope": {
                "type": "string",
                "description": "查询范围（1=最近文件），默认为 1",
                "default": "1",
            },
            "show_hidden": {
                "type": "string",
                "description": "是否显示隐藏文件（0/1），默认为 0",
                "default": "0",
            },
        },
        "required": [],
    }

    def handle(self, arguments: dict) -> str:
        return list_recent_files(
            start=arguments.get("start", "0"),
            num=arguments.get("num", "100"),
            scope=arguments.get("scope", "1"),
            show_hidden=arguments.get("show_hidden", "0"),
        )
