"""API 层 —— zspace NAS 的 HTTP 接口封装。

所有与 NAS 通信的逻辑集中在此，CLI 命令和 MCP 工具都调用此层，
避免重复编写请求逻辑。
"""

import json

import httpx

_client = httpx.Client(timeout=30)


class ApiError(RuntimeError):
    """API 业务错误（code 非 200）。"""

    def __init__(self, code: str, msg: str, data: dict | None = None):
        self.code = code
        self.msg = msg
        self.data = data
        super().__init__(f"[{code}] {msg}")


def _check_resp(resp: httpx.Response) -> dict | list:
    """检查 API 响应中的业务状态码。

    如果 code 非 "200" 则抛出 ApiError，否则返回 JSON 数据。

    Args:
        resp: httpx 响应对象。

    Returns:
        dict | list: 解析后的 JSON 数据。
    """
    data = resp.json()
    if isinstance(data, dict) and data.get("code") not in ("200", None):
        raise ApiError(
            code=data["code"],
            msg=data.get("msg", ""),
            data=data,
        )
    return data


def _resp_or_json(resp: httpx.Response, raw: bool) -> str | httpx.Response:
    """根据 raw 参数决定返回原始响应还是格式化 JSON 文本。

    Args:
        resp: httpx 响应对象。
        raw: 为 True 时返回原始 Response。

    Returns:
        str | httpx.Response: 格式化 JSON 字符串或原始响应。
    """
    if raw:
        return resp
    data = _check_resp(resp)
    return json.dumps(data, indent=2, ensure_ascii=False)

