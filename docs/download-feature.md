# 文件下载功能设计

## 背景

基于现有 `GET /v2/file/download` 端点实现文件下载功能。`read_file` 仅支持文本文件，`download_file` 不限文件类型。

## API 层

**文件：** `src/zspace/api/file.py`

```python
def download_file(path: str) -> bytes:
```

- 复用 `read_file` 的 `raw=True` 模式获取原始响应
- 不暴露端口、不限制扩展名
- 状态码非 200 时抛出 `ApiError`
- 只返回 `bytes`，不碰本地文件

## CLI 层

**文件：** `src/zspace/commands/download.py`

```
zcli download <path> <output_dir>
```

- `path`：NAS 文件路径（必填）
- `output_dir`：本地保存目录（必填）
- 文件名从 `path` 自动提取，写入 `output_dir/文件名`

## 使用方式

```bash
# 下载到当前目录
zcli download /sata12/my/data/photo.jpg .

# 下载到指定目录
zcli download /sata12/my/data/report.pdf ~/Downloads
```

## 不包含

- MCP 层不做（二进制数据不适合 MCP 的 `str` 返回）
- 端口不暴露给用户
