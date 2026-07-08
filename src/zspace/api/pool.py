"""存储池相关 API。"""

import httpx

from ..auth import build_headers, get_base_url
from . import _resp_or_json


def get_pool_info(raw: bool = False) -> str | httpx.Response:
    """获取存储池信息。

    Args:
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认返回 JSON 字符串；raw=True 时返回原始响应。
    """
    resp = httpx.request(
        "POST",
        f"{get_base_url()}/zspool/info",
        headers=build_headers(),
    )
    return _resp_or_json(resp, raw)
