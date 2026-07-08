"""文件相关 API。"""

import json
import time
import urllib.parse

import httpx

from ..auth import build_headers, get_base_url

from .fields import FILE_LIST


def _format_list_resp(resp: httpx.Response) -> str:
    """将文件列表 API 的缩写字段名映射为可读名称，并转换时间戳。"""
    raw = resp.json()
    out = []
    for item in raw:
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
    return resp if raw else _format_list_resp(resp)
