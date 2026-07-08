"""zspace API 字段名映射 —— 缩写 → 可读名称。

所有 API 接口的字段映射集中在此维护，方便统一管理和更新。
"""

FILE_LIST: dict[str, str] = {
    "n": "name",
    "di": "is_dir",
    "s": "size_bytes",
    "mt": "modified_at",
    "ct": "created_at",
    "is": "img_status",
    "dw": "downloading",
    "ns": "n_share",
    "pt": "part",
    "ec": "encrypted",
    "eci": "encrypt_icon",
    "ext": "extension",
    "height": "height",
    "weight": "width",
    "type": "mime_type",
    "is_sys": "is_system",
    "duration": "duration_ms",
    "ori": "orientation",
    "labels": "labels",
}
