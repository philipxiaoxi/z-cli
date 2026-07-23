"""teamlist 工具 —— AI 调用以列出团队空间（公共空间）目录中的文件。"""

from ...api.file import list_team_files
from ..base import McpTool


class ListTeamFilesTool(McpTool):
    name = "list_team_files"
    description = "列出 zspace NAS 团队空间（公共空间）目录下的文件与子文件夹"
    input_schema = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "团队空间目录路径，如 /public，默认 /public",
                "default": "/public",
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
        },
    }

    def handle(self, arguments: dict) -> str:
        return list_team_files(
            path=arguments.get("path", "/public"),
            start=arguments.get("start", "0"),
            num=arguments.get("num", "100"),
        )
