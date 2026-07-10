<div align="center">
  <h1>z-cli</h1>
  <p><em>zspace 私有云命令行工具 — CLI + MCP Server 双模式</em></p>

  <p>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
    <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows-lightgrey" alt="Platform">
    <img src="https://img.shields.io/badge/MCP-ready-purple?logo=matrix" alt="MCP">
  </p>
</div>

<div align="center">
  <img src="docs/intro.png" alt="z-cli 界面预览" width="800" />
</div>

## 概述

z-cli 是 zspace 私有云 NAS 的命令行工具，支持 **CLI** 和 **MCP Server** 两种使用方式。通过 MCP 协议接入 AI 助手后，可以用自然语言操控 NAS 上的文件和存储资源。

## 功能特性

- **文件操作** — 列表、创建、重命名、移动、复制、删除（回收站）
- **目录管理** — 创建文件夹，支持冲突自动重命名
- **文件搜索** — 按名称/类型/大小/时间搜索，支持分页
- **存储池查询** — 查看存储池信息和名称映射
- **最近文件** — 获取最近访问文件列表
- **MCP Server** — 通过 Model Context Protocol 暴露所有能力给 AI 助手
- **双模式运行** — 开发模式 `./dev`（热更新）与生产模式 `zcli`

## 接入 Agent 示例

将 z-cli 的 MCP Server 接入 AI 助手（如 opencode、Claude Code）后，用户可以通过自然语言直接操控 NAS。

下图为自研的 NAS 助手 Agent [z-agent](https://github.com/philipxiaoxi/z-agent) 的演示：

![z-cli 演示](docs/demo.png)

## 快速上手

### 前置条件

- **macOS / Windows**（认证模块从 zspace 桌面客户端本地数据目录读取凭据）
- Python >= 3.10
- zspace 桌面客户端已安装、登录，并保持在后台运行

### 安装

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1

pip install -e .

# 验证
zcli pool
```

### CLI 模式

```bash
# 存储池
zcli pool
zcli poolname

# 文件操作
zcli list /sata12/my/data
zcli mkdir /sata12/my/data 新建文件夹
zcli create /sata12/my/data/文件.txt
zcli rename /sata12/my/data/旧名称 新名称
zcli copy /sata12/my/data/a /sata12/my/data/b
zcli move /sata12/my/data/a /sata12/my/data/sub/
zcli remove /sata12/my/data/无用文件.txt

# 搜索与最近文件
zcli search 关键词
zcli recent

# 启动 MCP Server
zcli mcp
```

### MCP 模式

#### 推荐方式：pipx 全局安装

```bash
pipx install -e /path/to/zspace-cli
```

然后在 AI 工具（如 opencode、Claude Code）中配置：

```json
{
  "mcp": {
    "zspace-cli": {
      "type": "local",
      "command": ["zcli", "mcp"],
      "enabled": true
    }
  }
}
```

#### 备选方式：项目虚拟环境

```json
{
  "mcp": {
    "zspace-cli": {
      "type": "local",
      "command": [".venv/bin/python", "-m", "zspace", "mcp"],
      "enabled": true
    }
  }
}
```

> **注意**：macOS 可能对 `.venv` 下的文件自动设置隐藏标志，导致 Python 3.8+ 跳过 `__editable__` 的 `.pth` 文件（[CPython #113659](https://github.com/python/cpython/issues/113659)）。如果遇到 `ModuleNotFoundError: No module named 'zspace'` 错误，运行以下命令修复：
>
> ```bash
> xattr -rc .venv
> chflags -R 0 .venv
> ```

## 项目结构

```
z-cli/
├── .github/workflows/      # CI 配置
├── .claude/                # Claude 技能配置
├── src/zspace/
│   ├── api/                # NAS API 层
│   │   ├── fields.py       # 字段映射
│   │   ├── file.py         # 文件操作 API
│   │   └── pool.py         # 存储池 API
│   ├── commands/           # CLI 子命令
│   │   ├── base.py         # Command 基类
│   │   └── ...             # 每个命令一个文件
│   ├── mcp/                # MCP 服务器
│   │   ├── base.py         # McpTool 基类
│   │   └── tools/          # 每个工具一个文件
│   ├── auth.py             # 登录凭据读取
├── tests/                  # 测试
├── dev                     # 热更新运行脚本
├── Makefile                # 常用开发命令
├── CHANGELOG.md            # 变更日志
└── CONTRIBUTING.md         # 贡献指南
```

## CLI 命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `pool` | 查看存储池信息 | `zcli pool` |
| `poolname` | 查看存储池名称映射 | `zcli poolname` |
| `ping` | 检查与本地代理的连通性 | `zcli ping` |
| `list <path>` | 列出目录文件 | `zcli list /sata12/my/data` |
| `mkdir <parent> <name>` | 创建文件夹 | `zcli mkdir /sata12/my/data 新建` |
| `create <path>` | 创建文件 | `zcli create /sata12/my/data/a.txt` |
| `read <path>` | 读取文本文件内容 | `zcli read /sata12/my/data/a.txt` |
| `rename <path> <newname>` | 重命名 | `zcli rename /sata12/my/data/旧 新` |
| `copy <from> <to>` | 复制 | `zcli copy /sata12/a /sata12/b` |
| `move <from> <to>` | 移动 | `zcli move /sata12/a /sata12/b/` |
| `remove <path>` | 删除（回收站） | `zcli remove /sata12/my/data/文件.txt` |
| `search <keyword>` | 搜索文件 | `zcli search 会议记录` |
| `recent` | 最近文件 | `zcli recent` |
| `skills` | 管理 AI skills（install/uninstall） | `zcli skills install zspace-cli` |
| `mcp` | 启动 MCP Server | `zcli mcp` |

## MCP 工具列表

| 工具 | 功能 |
|------|------|
| `get_pool_info` | 查看存储池信息 |
| `get_pool_names` | 查看存储池名称映射 |
| `check_connectivity` | 检查与本地代理的连通性 |
| `list_files` | 列出目录文件 |
| `create_folder` | 创建文件夹 |
| `create_file` | 创建文件 |
| `read_file` | 读取文本文件内容 |
| `delete_item` | 删除文件/文件夹（移至回收站） |
| `rename_item` | 重命名 |
| `copy_item` | 复制 |
| `move_item` | 移动 |
| `search_files` | 搜索文件 |
| `list_recent_files` | 最近文件 |

## 存储池路径规则

访问文件路径格式为 `/<pool_name>/my/data`，其中 `pool_name` 是 `pool` 接口返回的 `name` 字段（如 `sata12`、`sata14`），不是 `id` 或系统挂载点。

## 配置

| 变量 | 说明 |
|------|------|
| `ZSPACE_HOST` | 覆盖 zspace 本地代理地址，用于跨网络访问 |

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 热更新模式（改源码即生效）
./dev pool

# 代码检查
make lint

# 运行测试
make test
```

## 致谢

本项目基于 [skyzhao1223/zspace-cli](https://github.com/skyzhao1223/zspace-cli) 的构思与想法，重新实现并调整了架构。

## 许可证

[MIT](LICENSE)
