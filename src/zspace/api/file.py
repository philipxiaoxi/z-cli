"""文件相关 API。"""

import json
import time
import urllib.parse

import httpx

from ..auth import build_headers, get_base_url

from . import _check_resp, _resp_or_json
from .fields import FILE_LIST


def _format_list(data: list) -> str:
    """将文件列表的缩写字段名映射为可读名称，并转换时间戳。"""
    out = []
    for item in data:
        readable = {}
        for short, val in item.items():
            long_name = FILE_LIST.get(short, short)
            if long_name in ("modified_at", "created_at") and isinstance(val, (int, float)) and val:
                readable[long_name] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(val))
            else:
                readable[long_name] = val
        out.append(readable)
    return json.dumps(out, indent=2, ensure_ascii=False)


def list_files(
    path: str,
    start: str = "0",
    num: str = "100",
    sortby: str = "mtime_linux",
    order: str = "desc",
    show_hidden: str = "0",
    dup: str = "0",
    with_fields: str = "encrypted,encrypt_icon,duration,nshare,ori,ext,height,weight,type,is_sys,dw,labels",
    raw: bool = False,
) -> str | httpx.Response:
    """列出 NAS 目录中的文件。

    Args:
        path: 目录路径。
        start: 分页起始偏移。
        num: 每页条目数。
        sortby: 排序字段。
        order: 排序方向 (asc/desc)。
        show_hidden: 是否显示隐藏文件 (0/1)。
        dup: 是否包含重复文件 (0/1)。
        with_fields: 返回的额外字段（逗号分隔）。
        raw: 为 True 时返回 httpx.Response，否则返回格式化 JSON 字符串。

    Returns:
        str | httpx.Response: 默认可读 JSON 字符串；raw=True 时返回原始响应。
    """
    data = {
        "start": start,
        "num": num,
        "sortby": sortby,
        "order": order,
        "path": path,
        "with_fields": with_fields,
        "show_hidden": show_hidden,
        "dup": dup,
    }
    resp = httpx.request(
        "POST",
        f"{get_base_url()}/v2/file/list/stream",
        headers=build_headers(path),
        content=urllib.parse.urlencode(data),
    )
    if raw:
        return resp
    raw_data = _check_resp(resp)
    return _format_list(raw_data) if isinstance(raw_data, list) else json.dumps(raw_data, indent=2, ensure_ascii=False)


def create_folder(parent: str, name: str, rename: str = "0", raw: bool = False) -> str | httpx.Response:
    """在 NAS 上创建新文件夹。

    Args:
        parent: 父目录路径。
        name: 文件夹名称。
        rename: 冲突时是否自动重命名 (0/1)。
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认返回 JSON 字符串；raw=True 时返回原始响应。
    """
    data = {
        "parent": parent,
        "name": name,
        "rename": rename,
    }
    resp = httpx.request(
        "POST",
        f"{get_base_url()}/v2/file/newdir",
        headers=build_headers(parent),
        content=urllib.parse.urlencode(data),
    )
    return _resp_or_json(resp, raw)
