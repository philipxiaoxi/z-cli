"""
认证模块 —— 从 zspace 桌面客户端读取登录凭据，
构建 HTTP 请求所需的 Cookie 和请求头。
"""

import json
import os
import sys
import urllib.parse
from pathlib import Path

# zspace 客户端本地数据目录
if sys.platform == "win32":
    ZSPACE_DIR = Path(os.environ["APPDATA"]) / "zspace"
elif sys.platform == "darwin":
    ZSPACE_DIR = Path.home() / "Library/Application Support/zspace"
else:
    ZSPACE_DIR = Path.home() / ".local/share/zspace"
# 集中状态文件 (Vuex 持久化)
VUEX_PATH = ZSPACE_DIR / "vuex.json"
# 设备配置
CONF_PATH = ZSPACE_DIR / "zspace.conf"


class AuthError(RuntimeError):
    """认证相关异常的基类。"""


# vuex.json 解析缓存，避免多次读取文件
_vuex_cache: dict | None = None


def _load_vuex() -> dict:
    """读取并缓存 vuex.json，返回 state 段。

    Raises:
        AuthError: 客户端目录或 vuex.json 不存在时。
    """
    global _vuex_cache
    if _vuex_cache is not None:
        return _vuex_cache
    if not ZSPACE_DIR.exists():
        raise AuthError("未找到 zspace 客户端数据目录，请安装 zspace 客户端并登录。")
    if not VUEX_PATH.exists():
        raise AuthError("zspace 客户端未登录，请先启动 zspace 客户端并登录。")
    with open(VUEX_PATH) as f:
        _vuex_cache = json.load(f).get("state", {})
    return _vuex_cache


def get_base_url() -> str:
    """获取 zspace 本地代理的基础 URL。

    优先使用 ZSPACE_HOST 环境变量覆盖（用于跨网络访问），
    否则从 vuex.json 的 app.localPort 读取监听端口。

    Returns:
        str: 格式如 "http://127.0.0.1:13579"。
    """
    override = os.environ.get("ZSPACE_HOST")
    if override:
        return override.rstrip("/")
    port = _load_vuex().get("app", {}).get("localPort", 13579)
    return f"http://127.0.0.1:{port}"


def build_cookies() -> dict[str, str]:
    """从 vuex.json 构建完整 Cookie 字典。

    所有值均为原始字符串，可能含中文/换行等非 ASCII 字符，
    调用方需自行编码后再放入 HTTP 请求头。

    Returns:
        dict[str, str]: Cookie 键值对。
    """
    vuex = _load_vuex()

    nas = vuex.get("nas", {})
    user = vuex.get("user", {})
    app = vuex.get("app", {})

    token = user.get("token", "")
    username = user.get("username", "")

    cookies = {
        # 认证令牌（两个字段值相同，服务端兼容）
        "zenithtoken": token,
        "token": token,
        # 与云端通信的 RSA 公钥及密钥 ID
        "cloudPubKey": nas.get("cloudPubKey", ""),
        "cloudPubKeyId": nas.get("cloudPubKeyId", ""),
        # 登录时下发的签名令牌
        "sign": nas.get("sign", ""),
        # 与 NAS 设备通信的 RSA 公钥
        "nasPubKey": nas.get("nasPubKey", ""),
        # 设备标识
        "device_id": app.get("deviceId", ""),
        # 用户信息
        "username": username,
        "qcname": user.get("qcname", ""),
        # NAS 设备信息
        "nas_id": nas.get("nasId", ""),
        "deviceColor": nas.get("color", ""),
        "devicePdt": nas.get("devicePdt", ""),
        "deviceMode": nas.get("deviceMode", ""),
        "isMaster": str(user.get("isMaster", "")),
        # 语言设置
        "_l": nas.get("locale", ""),
        # 以下字段在 vuex.json 中无持久化，使用固定值
        "version": "2.3.2026060701",
        "plat": "web",
        "app": "file",
        # 设备描述（含中文，由本模块自动编码）
        "device": app.get("device", ""),
    }
    return cookies


def build_cookie_header() -> str:
    """构建完整的 Cookie 请求头值。

    对所有值做 URL 编码，确保中文、换行符、特殊字符
    在 HTTP header 中合法。

    Returns:
        str: 格式如 "key1=val1; key2=val2" 的 Cookie 头值。
    """
    return "; ".join(
        f"{k}={urllib.parse.quote(v, safe='')}" for k, v in build_cookies().items()
    )


# 固定的 User-Agent，模拟 zspace 桌面客户端
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "zspace/2.41.2026061601 Netscape Electron/31.4.0"
)


def build_headers(path: str = "") -> dict[str, str]:
    """构建请求 zspace API 所需的标准请求头。

    包含 Cookie、Content-Type、Referer 和 User-Agent。
    Referer 中的 path 参数会被 URL 编码。

    Args:
        path: 当前访问的 NAS 文件路径，用于 Referer 拼接。

    Returns:
        dict[str, str]: 请求头字典。
    """
    base = get_base_url()
    return {
        "Cookie": build_cookie_header(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": (
            f"{base}/home/fileManage/myFiles"
            f"?path={urllib.parse.quote(path)}&v=2.3.2026060701"
        ),
        "User-Agent": USER_AGENT,
    }


if __name__ == "__main__":
    import pprint
    pprint.pprint(build_cookies())
