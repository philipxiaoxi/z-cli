# z-cli

## 提交规则

禁止直接推送。除非用户明确说明"推送到远程分支"或"push/publish"，否则只提交到本地分支。

## 项目技能

本项目包含一个项目级 skill，位于 `.claude/skills/zspace-coder/`，用于将抓包的 curl 请求自动转换为 CLI 命令和 MCP 工具。

当用户提供 curl 格式的请求时，会触发此 skill 引导完整的实现流程：解析 curl → API 函数 → CLI 命令 → MCP 工具 → 测试验证。

## 存储池路径规则

访问存储池文件的路径格式为 `/<pool_name>/my/data`，其中 `pool_name` 是 `pool` 接口返回的 `name` 字段（如 `sata12`、`sata14`），不是 `id` 或系统挂载点 `mnt`。

## 开发命令

```bash
./dev list <path>        # 列出文件
./dev pool               # 查看存储池
./dev mkdir <parent> <name>  # 创建文件夹
./dev rename <path> <newname> # 重命名
./dev mcp                # 启动 MCP 服务器
```
