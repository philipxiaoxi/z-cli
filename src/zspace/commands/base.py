"""命令基类与公共工具。"""

import json
import sys
from abc import ABC, abstractmethod

import httpx


def format_response(resp: httpx.Response):
    """格式化输出 HTTP 响应。

    优先 JSON 格式化输出，失败则输出原始文本。
    以非零状态码退出表示请求失败。

    Args:
        resp: httpx 响应对象。
    """
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text)
    sys.exit(0 if resp.is_success else 1)


class Command(ABC):
    """所有子命令的基类。

    子类需定义:
      - name:     子命令名称（用于 CLI 调用）
      - help:     帮助文本
      - register: 配置 argparse 参数
      - handle:   执行命令逻辑
    """

    name: str = ""
    help: str = ""

    @abstractmethod
    def register(self, parser):
        """注册 argparse 参数。

        Args:
            parser: add_subparsers 返回的子解析器。
        """

    @abstractmethod
    def handle(self, args):
        """执行命令。

        Args:
            args: argparse.Namespace 解析结果。
        """
