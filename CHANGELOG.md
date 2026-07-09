# Changelog

## [0.2.0] - 2026-07-09

### 新增

- 文件/文件夹创建（`create`），支持上传内容
- 文件/文件夹复制（`copy`），支持冲突自动重命名
- 文件/文件夹移动（`move`），支持冲突自动重命名
- 文件/文件夹删除（`remove`），移至回收站
- 文件搜索（`search`），支持多种排序和过滤
- 最近文件列表（`recent`）
- 存储池名称映射查看（`poolname`）
- AI skill 安装/卸载（`skills install` / `skills uninstall`）
- Windows 平台支持

### 变更

- 项目重命名为 `z-cli`，全部文本统一
- `cli.py` 合并进 `commands/__init__.py`，与 mcp 目录结构对齐
- httpx Client 单例复用，搜索接口超时设为 60s
- `remove` CLI 支持批量路径参数
- skill 安装路径从 cwd 改为 home 目录

### 移除

- `request` 命令（通用 HTTP 请求模块）
- `make_request` 功能和 `client.py` 模块
- MCP 中的 `request` 工具

### 修复

- pyproject.toml 中 `package_data` 改为 `package-data`，兼容新版 setuptools

## [0.1.0] - 2026-07-08

### 新增

- 存储池信息查看（`pool` / `poolname`）
- 文件列表查看（`list`），支持分页、排序、过滤
- 文件夹创建（`mkdir`），支持冲突自动重命名
- 文件创建（`create`），支持上传内容
- 文件/文件夹重命名（`rename`）
- 文件/文件夹移动（`move`），支持冲突自动重命名
- 文件/文件夹复制（`copy`），支持冲突自动重命名
- 文件/文件夹删除（`remove`），移至回收站
- 文件搜索（`search`），支持多种排序和过滤
- 最近文件列表（`recent`）
- 通用 HTTP 请求（`request`）
- MCP Server（`mcp`），暴露上述所有功能为 AI 工具

### 架构

- API 层集中封装 NAS 接口，支持 `raw` 模式返回原始响应
- CLI 命令基于 `Command` 基类注册模式，新增命令只需添加类引用
- MCP 工具基于 `McpTool` 基类注册模式，自动暴露给 AI 调用
- 认证模块从 zspace 客户端本地凭据自动构建 Cookie
- 支持热更新开发（`./dev` 脚本，改源码即生效）
- 生产安装（`pip install`，`zcli` 命令）

### 文档

- 项目级 CLAUDE.md 指导 AI 行为
- curl 请求转 CLI 命令的 zspace-coder skill
- 完整的 API、CLI、MCP 三层代码注释
