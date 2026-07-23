"""list_files 工具 —— AI 调用以列出 NAS 目录中的文件（支持个人空间和团队空间）。"""

from ...api.file import list_files, list_team_files
from ..base import McpTool


class ListFilesTool(McpTool):
    name = "list_files"
    description = "列出 zspace NAS 指定目录下的文件与子文件夹。设置 team=true 可列出团队空间文件"
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "目录路径。个人空间如 /sata12/my/data，团队空间如 /sata12/public",
            },
            "team": {
                "type": "boolean",
                "description": "是否列出团队空间文件，默认 false",
                "default": False,
            },
            "start": {
                "type": "string",
                "description": "分页起始偏移，默认 0",
                "default": "0",
            },
            "num": {
                "type": "string",
                "description": "每页条目数，默认 100",
                "default": "100",
            },
            "sortby": {
                "type": "string",
                "description": "排序字段，默认 mtime_linux（仅个人空间）",
                "default": "mtime_linux",
            },
            "order": {
                "type": "string",
                "enum": ["asc", "desc"],
                "description": "排序方向，默认 desc（仅个人空间）",
                "default": "desc",
            },
            "show_hidden": {
                "type": "string",
                "enum": ["0", "1"],
                "description": "是否显示隐藏文件，默认 0（仅个人空间）",
                "default": "0",
            },
        },
        "required": ["path"],
    }

    def handle(self, arguments: dict) -> str:
        if arguments.get("team", False):
            return list_team_files(
                path=arguments.get("path", "/public"),
                start=arguments.get("start", "0"),
                num=arguments.get("num", "100"),
            )
        return list_files(
            path=arguments["path"],
            start=arguments.get("start", "0"),
            num=arguments.get("num", "100"),
            sortby=arguments.get("sortby", "mtime_linux"),
            order=arguments.get("order", "desc"),
            show_hidden=arguments.get("show_hidden", "0"),
        )
