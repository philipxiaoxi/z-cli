"""用户相关 API。"""

import json
import urllib.parse

import httpx

from ..auth import build_headers, get_base_url
from . import _check_resp, _client


def get_pool_names(raw: bool = False) -> str | httpx.Response:
    """获取存储池名称映射（pool key → display name）。

    从用户列表中提取管理员可见的存储池列表。
    pool key（如 sata12）是路径中使用名称，display name（如"日立高速"）是别名。

    Args:
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认返回格式化的池名称映射 JSON；
                              raw=True 时返回原始响应。
    """
    data = {
        "all": "1",
    }
    resp = _client.request(
        "POST",
        f"{get_base_url()}/auth/user/list",
        headers=build_headers(),
        content=urllib.parse.urlencode(data),
    )
    if raw:
        return resp
    body = _check_resp(resp)
    raw_list = (body.get("data") or {}).get("list") or []
    pool_names = {}
    for user in raw_list:
        pn = user.get("pn") or []
        if pn:
            for entry in pn:
                pool_names[entry["k"]] = entry["n"]
            break
    return json.dumps(pool_names, indent=2, ensure_ascii=False)
