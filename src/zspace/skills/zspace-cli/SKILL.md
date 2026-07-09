---
name: zspace-cli
description: >
  用户需要操作 zspace 私有云 NAS 时触发。包括：列出文件、创建文件/文件夹、
  复制、移动、重命名、删除、搜索文件、查看存储池信息等。
  AI 通过执行 `zcli <command>` 命令行完成操作，无需 MCP 服务器。
  适用于所有文件管理和存储池查询场景。
---

# zspace CLI 使用指南

本项目的 CLI 入口为 `zcli`（`./dev` 仅用于开发热更新），所有 NAS 操作均通过 `zcli <子命令>` 完成。

## 路径规则

访问存储池文件的路径格式为 `/<pool_name>/my/data`，其中 `pool_name` 是 `poolname` 命令返回的 `name` 字段（如 `sata12`、`sata14`），**不是** `id` 或系统挂载点 `mnt`。

## 命令参考

### 文件与文件夹操作

| 命令 | 功能 | 示例 |
|------|------|------|
| `list` | 列出目录内容 | `zcli list /sata12/my/data` |
| `mkdir` | 创建文件夹 | `zcli mkdir /sata12/my/data 新文件夹` |
| `create` | 创建文件（可选内容） | `zcli create /sata12/my/data/test.txt --content "hello"` |
| `copy` | 复制（支持多源） | `zcli copy /sata12/a,/sata12/b /sata12/dst/` |
| `move` | 移动（支持多源） | `zcli move /sata12/a,/sata12/b /sata12/dst/` |
| `rename` | 重命名 | `zcli rename /sata12/my/data/旧名 新名` |
| `remove` | 删除（支持多源，移至回收站） | `zcli remove /sata12/a,/sata12/b` |
| `search` | 搜索文件 | `zcli search 关键词 --path /sata12/my/data` |
| `recent` | 最近访问文件 | `zcli recent --num 20` |

> 多源参数通过逗号分隔（无空格）：`copy`、`move`、`remove` 支持同时操作多个路径。

### 存储池

| 命令 | 功能 | 示例 |
|------|------|------|
| `pool` | 查看存储池信息 | `zcli pool` |
| `poolname` | 查看名称映射 | `zcli poolname` |

### 其他

| 命令 | 功能 | 示例 |
|------|------|------|
| `mcp` | 启动 MCP 服务器 | `zcli mcp` |

## 常用参数

- `--rename 0/1` — 文件冲突时自动重命名（copy/move/mkdir/create）
- `--show-hidden 0/1` — 是否包含隐藏文件
- `--order asc/desc` — 排序方向
- `--sortby <字段>` — 排序字段（默认 `mtime_linux`）
- `--start <偏移>` / `--num <数量>` — 分页控制

## 路径规范

- 所有路径必须以 pool name 开头（如 `/sata12/...`），不是挂载点 `/mnt/...`
