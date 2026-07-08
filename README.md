# ZSpace CLI

基于 Python 的 HTTP 请求工具，支持 **CLI 命令行** 和 **MCP Server** 两种使用方式。

## 快速上手

```bash
# 激活虚拟环境
source .venv/bin/activate

# CLI 模式 — 发起 HTTP 请求
zcli request get  https://api.example.com/data
zcli request post https://api.example.com/data -d '{"key":"value"}'
zcli request get  https://api.example.com/data -H "Authorization:Bearer xxx"

# MCP Server 模式 — 通过 stdio 对外提供 make_request 工具
zcli mcp
```

## 目录结构

```
zspace-cli/
├── .venv/                  # Python 虚拟环境
├── .gitignore
├── pyproject.toml          # 项目元信息 + 依赖声明
├── README.md
└── src/zspace/
    ├── __init__.py
    ├── client.py           # 核心: httpx 封装，所有请求逻辑在此
    ├── cli.py              # CLI 入口, 解析命令行参数, 调度到 client / mcp
    └── mcp_server.py       # MCP Server 定义, 注册 make_request 工具
```

## 上手开发

### 热更新模式（推荐）

```bash
./dev request get https://api.example.com/data
./dev mcp
```

`./dev` 脚本自动设置 `PYTHONPATH`，修改源码后**无需重装**，直接运行即可。

### 生产安装模式

```bash
.venv/bin/pip install . --force-reinstall
zcli request get https://api.example.com/data
```

> Python 3.14 暂不支持 `pip install -e .`，生产安装需执行完整安装。

### 模块职责

| 模块 | 职责 |
|------|------|
| `client.py` | 只做一件事：发 HTTP 请求。被 cli 和 mcp 共同调用 |
| `cli.py` | 解析终端参数，转发给 client 或启动 mcp server |
| `mcp_server.py` | 注册 MCP tools，让 LLM 通过 MCP 协议调用请求能力 |
