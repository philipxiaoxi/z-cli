---
name: zspace-mcp
description: >
  用户需要操作 zspace 私有云 NAS 时触发，zspace MCP 服务器已就绪可直接调用工具。
  包括：列出文件、创建文件/文件夹、复制、移动、重命名、删除、搜索文件、
  查看存储池信息等。AI 通过调用 MCP 工具完成操作，无需执行 CLI 命令。
  适用于 MCP 配置就绪场景下的所有文件管理和存储池查询。
---

# zspace MCP 工具指南

本项目内置 MCP Server，将 zspace NAS 的所有操作暴露为标准 MCP 工具。

> 如果 AI 未找到 zspace 相关的 MCP 工具，请告诉用户需要在 AI 客户端的 MCP 配置中添加：
> `{"mcpServers": {"zspace": {"command": "zcli", "args": ["mcp"]}}}`

## 路径规则

访问存储池文件的路径格式为 `/<pool_name>/my/data`，其中 `pool_name` 是 `get_pool_names` 工具返回的 `name` 字段（如 `sata12`、`sata14`），**不是** `id` 或系统挂载点 `mnt`。

## 可用工具

### 文件与文件夹操作

| 工具名 | 功能 | 关键参数 |
|--------|------|---------|
| `list_files` | 列出目录内容 | `path`（必填）, `start`, `num`, `sortby`, `order`, `show_hidden` |
| `create_folder` | 创建文件夹 | `parent`（必填）, `name`（必填）, `rename` |
| `create_file` | 创建文件 | `path`（必填）, `content`, `rename` |
| `copy_item` | 复制（支持多源） | `paths`（必填，字符串数组）, `to`（必填）, `rename` |
| `move_item` | 移动（支持多源） | `paths`（必填，字符串数组）, `to`（必填）, `rename` |
| `rename_item` | 重命名 | `path`（必填）, `newname`（必填） |
| `delete_item` | 删除（支持多源，移至回收站） | `paths`（必填，字符串数组）, `show_hidden` |
| `search_files` | 搜索文件 | `name`（必填）, `file_path`, `ftype`, `is_dir`, `min_size`, `max_size` |
| `list_recent_files` | 最近访问文件 | `start`, `num` |

### 存储池

| 工具名 | 功能 |
|--------|------|
| `get_pool_info` | 查看存储池信息 |
| `get_pool_names` | 获取存储池名称映射 |

## 路径规范

- 所有路径必须以 pool name 开头（如 `/sata12/...`），不是挂载点 `/mnt/...`
