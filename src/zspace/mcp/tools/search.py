"""search 工具 —— AI 调用以搜索 NAS 上的文件。"""

from ...api.file import search_files
from ..base import McpTool


class SearchTool(McpTool):
    name = "search_files"
    description = "在zspace NAS 上搜索文件"
    input_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "搜索关键词",
            },
            "file_path": {
                "type": "string",
                "description": "搜索范围路径，如 /sata12/my/data",
                "default": "/sata12/my/data",
            },
            "order_by": {
                "type": "string",
                "enum": ["0", "1", "2"],
                "description": "排序方式 (0=名称, 1=修改时间, 2=大小)",
                "default": "0",
            },
            "ftype": {
                "type": "string",
                "description": "文件类型筛选",
                "default": "",
            },
            "is_dir": {
                "type": "string",
                "enum": ["", "0", "1"],
                "description": "是否仅目录",
                "default": "",
            },
            "min_size": {
                "type": "string",
                "description": "最小文件大小（字节）",
                "default": "0",
            },
            "max_size": {
                "type": "string",
                "description": "最大文件大小（字节）",
                "default": "0",
            },
            "start": {
                "type": "string",
                "description": "分页起始偏移",
                "default": "0",
            },
            "num": {
                "type": "string",
                "description": "每页条目数",
                "default": "30",
            },
            "shared_only": {
                "type": "string",
                "enum": ["0", "1"],
                "description": "仅搜索共享文件",
                "default": "0",
            },
            "show_hidden": {
                "type": "string",
                "enum": ["0", "1"],
                "description": "是否显示隐藏文件",
                "default": "0",
            },
        },
        "required": ["name"],
    }

    def handle(self, arguments: dict) -> str:
        return search_files(
            name=arguments["name"],
            file_path=arguments.get("file_path", "/sata12/my/data"),
            order_by=arguments.get("order_by", "0"),
            ftype=arguments.get("ftype", ""),
            is_dir=arguments.get("is_dir", ""),
            min_size=arguments.get("min_size", "0"),
            max_size=arguments.get("max_size", "0"),
            start=arguments.get("start", "0"),
            num=arguments.get("num", "30"),
            shared_only=arguments.get("shared_only", "0"),
            show_hidden=arguments.get("show_hidden", "0"),
        )
