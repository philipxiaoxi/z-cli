"""简单的 HTTP 客户端封装，基于 httpx。"""

import httpx


def request(method: str, url: str, **kwargs) -> httpx.Response:
    """发送 HTTP 请求。

    Args:
        method: HTTP 方法 (GET/POST/PUT/DELETE/PATCH 等，大小写不敏感)。
        url: 目标 URL。
        **kwargs: 传递给 httpx.Client.request 的额外参数。

    Returns:
        httpx.Response: 服务器响应。
    """
    with httpx.Client(timeout=30) as client:
        return client.request(method.upper(), url, **kwargs)
