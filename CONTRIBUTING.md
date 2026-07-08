# 贡献指南

感谢你考虑为 zspace-cli 做出贡献！

## 开发环境

```bash
# 克隆项目
git clone <your-fork>
cd zspace-cli

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"
```

## 代码规范

- Python >= 3.10
- 遵循现有代码风格
- 所有函数/类需有类型注解和中文 docstring
- API 层函数需支持 `raw` 参数

## 新增命令流程

1. API 层：在 `src/zspace/api/` 中实现 NAS 接口调用
2. CLI 命令：在 `src/zspace/commands/` 中实现，继承 `Command` 基类
3. MCP 工具：在 `src/zspace/mcp/tools/` 中实现，继承 `McpTool` 基类
4. 注册：在 `commands/__init__.py` 和 `mcp/tools/__init__.py` 中注册

## 提交规范

使用 Conventional Commits 格式：

- `feat:` — 新功能
- `fix:` — Bug 修复
- `refactor:` — 重构
- `docs:` — 文档
- `chore:` — 构建/工具链

## 测试

```bash
# 运行测试
make test

# 运行 lint
make lint
```

## Pull Request

1. Fork 项目并创建特性分支
2. 提交你的修改
3. 确保测试通过
4. 发起 PR 到 `main` 分支
