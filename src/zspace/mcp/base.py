"""MCP 工具基类 —— 所有工具的抽象接口。"""

from abc import ABC, abstractmethod

import mcp.types as types


class McpTool(ABC):
    """MCP 工具基类。

    子类需定义:
      - name:          工具名称（AI 调用时使用）
      - description:   工具描述（AI 理解用途）
      - input_schema:  参数 JSON Schema（约束参数格式）
      - handle:        执行工具逻辑
    """

    name: str = ""
    description: str = ""
    input_schema: dict = {}

    @abstractmethod
    def handle(self, arguments: dict) -> str:
        """执行工具并返回结果文本。

        Args:
            arguments: 符合 input_schema 的参数字典。

        Returns:
            str: 响应文本（通常是 JSON 格式）。
        """

    def to_mcp_tool(self) -> types.Tool:
        """转换为 MCP SDK 的 Tool 定义。"""
        return types.Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema,
        )
