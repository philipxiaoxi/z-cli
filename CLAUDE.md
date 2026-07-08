# zspace-cli

## 项目技能

本项目包含一个项目级 skill，位于 `.claude/skills/zspace-coder/`，用于将抓包的 curl 请求自动转换为 CLI 命令和 MCP 工具。

当用户提供 curl 格式的请求时，会触发此 skill 引导完整的实现流程：解析 curl → API 函数 → CLI 命令 → MCP 工具 → 测试验证。

## 开发命令

```bash
./dev list <path>        # 列出文件
./dev pool               # 查看存储池
./dev mkdir <parent> <name>  # 创建文件夹
./dev rename <path> <newname> # 重命名
./dev mcp                # 启动 MCP 服务器
```
