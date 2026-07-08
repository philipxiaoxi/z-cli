import os
import json
import urllib.parse
from pathlib import Path

ZSPACE_DIR = Path.home() / "Library/Application Support/zspace"
VUEX_PATH = ZSPACE_DIR / "vuex.json"
CONF_PATH = ZSPACE_DIR / "zspace.conf"


class AuthError(RuntimeError):
    pass


_vuex_cache: dict | None = None


def _load_vuex():
    global _vuex_cache
    if _vuex_cache is not None:
        return _vuex_cache
    if not ZSPACE_DIR.exists():
        raise AuthError("未找到zspace客户端数据目录，请安装zspace客户端并登录。")
    if not VUEX_PATH.exists():
        raise AuthError("zspace客户端未登录，请先启动zspace客户端并登录。")
    with open(VUEX_PATH) as f:
        _vuex_cache = json.load(f).get("state", {})
    return _vuex_cache


def get_base_url() -> str:
    override = os.environ.get("ZSPACE_HOST")
    if override:
        return override.rstrip("/")
    port = _load_vuex().get("app", {}).get("localPort", 13579)
    return f"http://127.0.0.1:{port}"


def build_cookies() -> dict[str, str]:
    vuex = _load_vuex()

    nas = vuex.get("nas", {})
    user = vuex.get("user", {})
    app = vuex.get("app", {})

    token = user.get("token", "")
    username = user.get("username", "")

    cookies = {
        "zenithtoken": token,
        "token": token,
        "cloudPubKey": nas.get("cloudPubKey", ""),
        "cloudPubKeyId": nas.get("cloudPubKeyId", ""),
        "sign": nas.get("sign", ""),
        "nasPubKey": nas.get("nasPubKey", ""),
        "device_id": app.get("deviceId", ""),
        "username": username,
        "qcname": user.get("qcname", ""),
        "nas_id": nas.get("nasId", ""),
        "deviceColor": nas.get("color", ""),
        "devicePdt": nas.get("devicePdt", ""),
        "deviceMode": nas.get("deviceMode", ""),
        "isMaster": str(user.get("isMaster", "")),
        "_l": nas.get("locale", ""),
        "version": "2.3.2026060701",
        "plat": "web",
        "app": "file",
        "device": app.get("device", ""),
    }
    return cookies


def build_cookie_header() -> str:
    return "; ".join(
        f"{k}={urllib.parse.quote(v, safe='')}" for k, v in build_cookies().items()
    )


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "zspace/2.41.2026061601 Netscape Electron/31.4.0"
)


def build_headers(path: str = "") -> dict[str, str]:
    base = get_base_url()
    return {
        "Cookie": build_cookie_header(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"{base}/home/fileManage/myFiles?path={urllib.parse.quote(path)}&v=2.3.2026060701",
        "User-Agent": USER_AGENT,
    }


if __name__ == "__main__":
    import pprint
    pprint.pprint(build_cookies())
