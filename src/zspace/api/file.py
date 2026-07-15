"""文件相关 API。"""

import json
import time
import urllib.parse

import httpx

from ..auth import build_headers, get_base_url
from . import ApiError, _check_resp, _client, _resp_or_json
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
    resp = _client.request(
        "POST",
        f"{get_base_url()}/v2/file/list/stream",
        headers=build_headers(path),
        content=urllib.parse.urlencode(data),
    )
    if raw:
        return resp
    raw_data = _check_resp(resp)
    return _format_list(raw_data) if isinstance(raw_data, list) else json.dumps(raw_data, indent=2, ensure_ascii=False)


def delete_item(paths: str | list[str], show_hidden: bool = False, raw: bool = False) -> str | httpx.Response:
    """删除 NAS 上的文件或文件夹（移至回收站）。

    Args:
        paths: 要删除的文件/文件夹路径，可以是单个路径字符串或路径列表。
        show_hidden: 是否包含隐藏文件。
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认返回 JSON 字符串；raw=True 时返回原始响应。
    """
    if isinstance(paths, str):
        paths = [paths]
    data = {
        "paths[]": paths,
        "skip_bin": "0",
        "show_hidden": "1" if show_hidden else "0",
    }
    resp = _client.request(
        "POST",
        f"{get_base_url()}/v2/file/remove",
        headers=build_headers(paths[0] if paths else ""),
        content=urllib.parse.urlencode(data, doseq=True),
    )
    return _resp_or_json(resp, raw)


def rename_item(path: str, newname: str, raw: bool = False) -> str | httpx.Response:
    """重命名 NAS 上的文件或文件夹。

    Args:
        path: 文件/文件夹的完整路径。
        newname: 新名称（仅文件名，不包含路径）。
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认返回 JSON 字符串；raw=True 时返回原始响应。
    """
    data = {
        "path": path,
        "newname": newname,
    }
    resp = _client.request(
        "POST",
        f"{get_base_url()}/v2/file/modify",
        headers=build_headers(path),
        content=urllib.parse.urlencode(data),
    )
    return _resp_or_json(resp, raw)


def move_item(paths: str | list[str], to: str, rename: str = "0", raw: bool = False) -> str | httpx.Response:
    """移动或重命名 NAS 上的文件或文件夹。

    Args:
        paths: 要移动的文件/文件夹路径，可以是单个路径字符串或路径列表。
        to: 目标路径，可以是目录路径或新路径。
        rename: 冲突时是否自动重命名 (0/1)。
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认返回 JSON 字符串；raw=True 时返回原始响应。
    """
    if isinstance(paths, str):
        paths = [paths]
    data = {
        "paths[]": paths,
        "to": to,
        "rename": rename,
    }
    resp = _client.request(
        "POST",
        f"{get_base_url()}/v2/file/move",
        headers=build_headers(paths[0] if paths else ""),
        content=urllib.parse.urlencode(data, doseq=True),
    )
    return _resp_or_json(resp, raw)


def copy_item(paths: str | list[str], to: str, rename: str = "0", raw: bool = False) -> str | httpx.Response:
    """复制 NAS 上的文件或文件夹。

    Args:
        paths: 要复制的源路径，可以是单个路径字符串或路径列表。
        to: 目标路径。
        rename: 冲突时是否自动重命名 (0/1)。
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认返回 JSON 字符串；raw=True 时返回原始响应。
    """
    if isinstance(paths, str):
        paths = [paths]
    data = {
        "paths[]": paths,
        "to": to,
        "rename": rename,
    }
    resp = _client.request(
        "POST",
        f"{get_base_url()}/v2/file/copy",
        headers=build_headers(paths[0] if paths else ""),
        content=urllib.parse.urlencode(data, doseq=True),
    )
    return _resp_or_json(resp, raw)


def list_recent_files(
    start: str = "0",
    num: str = "100",
    scope: str = "1",
    show_hidden: str = "0",
    with_fields: str = "encrypted,encrypt_icon,duration,nshare,ori,ext,height,weight,type,is_sys,dw,labels",
    raw: bool = False,
) -> str | httpx.Response:
    """获取 NAS 上最近访问的文件列表。

    Args:
        start: 分页起始偏移。
        num: 每页条目数。
        scope: 查询范围 (1=最近文件)。
        show_hidden: 是否显示隐藏文件 (0/1)。
        with_fields: 返回的额外字段（逗号分隔）。
        raw: 为 True 时返回 httpx.Response，否则返回格式化 JSON 字符串。

    Returns:
        str | httpx.Response: 默认可读 JSON 字符串；raw=True 时返回原始响应。
    """
    data = {
        "start": start,
        "num": num,
        "scope": scope,
        "with_fields": with_fields,
        "show_hidden": show_hidden,
    }
    resp = _client.request(
        "POST",
        f"{get_base_url()}/v2/file/latest/list",
        headers=build_headers(""),
        content=urllib.parse.urlencode(data),
    )
    if raw:
        return resp
    raw_data = _check_resp(resp)
    return _format_list(raw_data) if isinstance(raw_data, list) else json.dumps(raw_data, indent=2, ensure_ascii=False)


def create_file(path: str, rename: str = "0", content: bytes = b"", raw: bool = False) -> str | httpx.Response:
    """在 NAS 上创建文件。

    Args:
        path: 文件完整路径。
        rename: 冲突时是否自动重命名 (0/1)。
        content: 文件内容（二进制），默认为空。
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认返回 JSON 字符串；raw=True 时返回原始响应。
    """
    parent_path = path.rsplit("/", 1)[0] if "/" in path else ""
    headers = build_headers(parent_path)
    headers["Content-Type"] = "application/octet-stream"
    headers["rename"] = rename
    headers["path"] = urllib.parse.quote(path, safe="")
    resp = _client.request(
        "POST",
        f"{get_base_url()}/v2/file/create",
        headers=headers,
        content=content,
    )
    return _resp_or_json(resp, raw)


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
    resp = _client.request(
        "POST",
        f"{get_base_url()}/v2/file/newdir",
        headers=build_headers(parent),
        content=urllib.parse.urlencode(data),
    )
    return _resp_or_json(resp, raw)


_TEXT_EXTENSIONS = frozenset({
    ".md", ".txt", ".json", ".yaml", ".yml", ".xml", ".csv", ".toml", ".ini",
    ".cfg", ".conf", ".env", ".gitignore", ".dockerignore", ".editorconfig",
    ".js", ".ts", ".jsx", ".tsx", ".py", ".rb", ".go", ".rs", ".java", ".c",
    ".cpp", ".h", ".hpp", ".css", ".scss", ".less", ".html", ".htm", ".vue",
    ".svelte", ".php", ".sh", ".bash", ".zsh", ".ps1", ".bat", ".sql",
    ".log", ".svg", ".lock", ".gradle", ".properties", ".makefile",
})


def read_file(path: str, remote_port: str = "8050", raw: bool = False) -> str | httpx.Response:
    """读取 NAS 上文本文件的内容（仅限文本文件，非文本文件返回错误）。

    Args:
        path: 文件完整路径。
        remote_port: NAS web 服务端口，默认 8050。
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认可读文本内容或错误信息；raw=True 时返回原始响应。
    """
    parent_path = path.rsplit("/", 1)[0] if "/" in path else ""
    params = {
        "path": path,
        "remote_port": remote_port,
        "request_purpose": "5",
    }
    resp = _client.request(
        "GET",
        f"{get_base_url()}/v2/file/download",
        headers=build_headers(parent_path),
        params=params,
    )
    if raw:
        return resp

    if resp.status_code != 200:
        return f"错误：服务器返回状态码 {resp.status_code}"

    ext = (path.rsplit(".", 1)[-1] if "." in path else "").lower()
    if ext and f".{ext}" not in _TEXT_EXTENSIONS:
        return f"错误：不支持读取非文本文件（.{ext}）"

    return resp.text


def search_files(
    name: str,
    file_path: str,
    order_by: str = "0",
    ftype: str = "",
    is_dir: str = "",
    min_size: str = "0",
    max_size: str = "0",
    start: str = "0",
    num: str = "30",
    shared_only: str = "0",
    show_hidden: str = "0",
    raw: bool = False,
) -> str | httpx.Response:
    """搜索 NAS 上的文件。

    Args:
        name: 搜索关键词。
        file_path: 搜索范围路径。
        order_by: 排序方式 (0=名称, 1=修改时间, 2=大小)。
        ftype: 文件类型筛选。
        is_dir: 是否仅目录 (0/1)。
        min_size: 最小文件大小（字节）。
        max_size: 最大文件大小（字节）。
        start: 分页起始偏移。
        num: 每页条目数。
        shared_only: 仅搜索共享文件 (0/1)。
        show_hidden: 是否显示隐藏文件 (0/1)。
        raw: 为 True 时返回 httpx.Response。

    Returns:
        str | httpx.Response: 默认可读 JSON 字符串；raw=True 时返回原始响应。
    """
    data = {
        "name": name,
        "file_path": file_path,
        "order_by": order_by,
        "ftype": ftype,
        "is_dir": is_dir,
        "min_size": min_size,
        "max_size": max_size,
        "start": start,
        "num": num,
        "shared_only": shared_only,
        "show_hidden": show_hidden,
    }
    resp = _client.request(
        "POST",
        f"{get_base_url()}/file_search/file_search",
        headers=build_headers(file_path),
        content=urllib.parse.urlencode(data),
        timeout=60,
    )
    if raw:
        return resp
    raw_data = _check_resp(resp)
    return _format_list(raw_data) if isinstance(raw_data, list) else json.dumps(raw_data, indent=2, ensure_ascii=False)


def download_file(path: str) -> bytes:
    """下载 NAS 上的文件（不限类型），返回二进制内容。

    Args:
        path: 文件完整路径。

    Returns:
        bytes: 文件的二进制内容。

    Raises:
        ApiError: 下载失败时抛出。
    """
    resp = read_file(path, raw=True)
    assert isinstance(resp, httpx.Response)
    if resp.status_code != 200:
        raise ApiError(str(resp.status_code), f"下载失败，状态码 {resp.status_code}")
    return resp.content


