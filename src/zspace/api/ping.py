"""连通性检测 API。"""

import json
import time

import httpx

from ..auth import get_base_url


def ping(timeout: int = 5) -> str:
    """检查与 zspace 本地代理的连通性。

    检测步骤：
    1. TCP 连接测试
    2. HTTP 响应测试
    3. 响应时间测量

    Args:
        timeout: 超时秒数，默认 5。

    Returns:
        str: JSON 格式的检测结果。
    """
    base_url = get_base_url()
    result = {"host": base_url, "timestamp": int(time.time())}

    start = time.time()
    try:
        resp = httpx.get(base_url, timeout=timeout)
        elapsed = time.time() - start
        result["response_time_ms"] = round(elapsed * 1000)
        result["status_code"] = resp.status_code
        result["status"] = "connected"
    except httpx.ConnectError:
        elapsed = time.time() - start
        result["response_time_ms"] = round(elapsed * 1000)
        result["status"] = "unreachable"
        result["error"] = "无法连接到本地代理，请确认 zspace 客户端已启动并登录"
    except httpx.TimeoutException:
        result["response_time_ms"] = timeout * 1000
        result["status"] = "timeout"
        result["error"] = f"连接超时（{timeout}秒）"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return json.dumps(result, indent=2, ensure_ascii=False)
