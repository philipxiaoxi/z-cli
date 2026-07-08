# ZSpace CLI

zspace私有云命令行工具，支持 **CLI** 和 **MCP Server** 两种使用方式。

## 快速上手

```bash
# 热更新模式（开发推荐，改源码即生效）
./dev pool                              # 查看存储池信息
./dev poolname                          # 查看存储池名称映射
./dev list /sata12/my/data              # 列出目录文件
./dev mkdir /sata12/my/data 新建文件夹   # 创建文件夹
./dev create /sata12/my/data/文件.txt    # 创建文件
./dev rename /sata12/my/data/旧名称 新名称
./dev copy  /sata12/my/data/a /sata12/my/data/b
./dev move  /sata12/my/data/a /sata12/my/data/sub/
./dev remove /sata12/my/data/无用文件.txt
./dev search 关键词                      # 搜索文件
./dev recent                             # 最近文件
./dev request get https://api.example.com
./dev mcp                                # 启动 MCP Server

# 生产安装模式（安装后直接用 zcli 命令）
.venv/bin/pip install .
zcli pool
zcli list /sata12/my/data
```

## MCP 配置

在 `opencode.json` 中添加 MCP Server 配置：

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

启动后提供以下 MCP 工具：

| 工具 | 功能 |
|------|------|
| `get_pool_info` | 查看存储池信息 |
| `get_pool_names` | 查看存储池名称映射 |
| `list_files` | 列出目录文件 |
| `create_folder` | 创建文件夹 |
| `create_file` | 创建文件 |
| `delete_item` | 删除文件/文件夹（移至回收站） |
| `rename_item` | 重命名 |
| `copy_item` | 复制 |
| `move_item` | 移动 |
| `search_files` | 搜索文件 |
| `list_recent_files` | 最近文件 |
| `make_request` | 通用 HTTP 请求 |

## 存储池路径规则

访问文件路径格式为 `/<pool_name>/my/data`，其中 `pool_name` 是 `pool` 接口返回的 `name` 字段（如 `sata12`、`sata14`），不是 `id` 或系统挂载点。

## 目录结构

```
zspace-cli/
├── .venv/                     # Python 虚拟环境
├── .claude/                   # Claude 技能配置
├── CLAUDE.md                  # 项目级 AI 指令
├── dev                        # 热更新运行脚本
├── pyproject.toml
└── src/zspace/
    ├── __init__.py
    ├── __main__.py            # python -m zspace 入口
    ├── auth.py                # 从zspace客户端读取登录凭据
    ├── cli.py                 # CLI 入口，命令分发
    ├── client.py              # httpx 封装
    ├── api/                   # NAS API 层
    │   ├── fields.py          # 字段映射
    │   ├── file.py            # 文件操作 API
    │   ├── pool.py            # 存储池 API
    │   └── user.py            # 用户相关 API
    ├── commands/              # CLI 子命令（每个文件一个命令）
    ├── mcp/                   # MCP 服务器
    │   ├── __init__.py        # 服务器启动 + 工具路由
    │   ├── base.py            # McpTool 基类
    │   └── tools/             # MCP 工具（每个文件一个工具）
```

## 开发

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
.venv/bin/pip install -e .

# 直接运行（改源码即生效）
./dev pool
./dev mcp
```
