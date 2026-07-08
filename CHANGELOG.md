# Changelog

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
- 认证模块从zspace客户端本地凭据自动构建 Cookie
- 支持热更新开发（`./dev` 脚本，改源码即生效）
- 生产安装（`pip install`，`zcli` 命令）

### 文档

- 项目级 CLAUDE.md 指导 AI 行为
- curl 请求转 CLI 命令的 zspace-coder skill
- 完整的 API、CLI、MCP 三层代码注释
