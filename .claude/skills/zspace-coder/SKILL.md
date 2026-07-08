---
name: zspace-coder
description: >
  将抓包的 curl 请求自动转换为zspace CLI 命令和 MCP 工具的完整功能。
  当用户提供 curl 命令（来自浏览器开发者工具 Network 面板的请求复制），
  需要解析并生成对应的 API 层函数、CLI 子命令、MCP 工具和字段映射，
  并用 /sata14/my/data/测试文件夹 验证功能是否正常。
  涉及的具体操作包括：文件操作（列表/创建/删除/重命名/移动/上传/下载）、
  存储池管理、系统信息、用户管理、备份恢复等所有zspace NAS API。
  只要是 curl 命令格式的请求，都应该触发此 skill。

  注意：测试时只允许使用 /sata14/my/data/测试文件夹 这个目录，
  禁止在任何其他路径创建/修改/删除文件。
---

## 项目信息

- 项目根目录：`/Users/philip/Documents/code/zspace-cli`
- 开发运行：`./dev <command> <args>`（热更新，改代码直接生效）
- API 模块：`src/zspace/api/`
- CLI 模块：`src/zspace/commands/`
- MCP 模块：`src/zspace/mcp/tools/`


## 工作流程

收到 curl 命令后，按以下步骤执行：

### 第一步：解析 curl

从 curl 命令中提取关键信息：

1. **URL 路径** — 去掉协议/域名/端口，只保留路径部分。
   例如 `http://127.0.0.1:13579/v2/file/newdir` → `/v2/file/newdir`
   去掉 URL 中 `rnd` 和 `webagent` 等反缓存查询参数。

2. **HTTP 方法** — 从 `-X` 参数获取。如果没有 `-X` 但有 `--data-raw`，默认为 POST。

3. **请求体参数** — 从 `--data-raw` 中解析。`urllib.parse.urlencode(data)` 会自动处理编码，
   所以在代码中直接传原始字符串（不要手动 URL 编码）。

4. **Referer 路径** — 从 `-H 'Referer: ...'` 中提取 `path=` 查询参数的值，
   用于 `build_headers()` 的 path 参数。

5. **响应字段** — 如果响应包含缩写字段（如 `n`、`di`、`s`、`mt` 等），需要创建字段映射。


### 第二步：确认无重复

检查以下目录现有文件，确认没有重复实现：

- `src/zspace/api/` — API 函数
- `src/zspace/commands/` — CLI 命令
- `src/zspace/mcp/tools/` — MCP 工具

新增代码前看一两个现有实现，确保风格一致。


### 第三步：实现 API 函数

根据 curl 在 `src/zspace/api/` 下创建或修改 API 函数。

**模板：**

```python
"""模块描述。"""

import urllib.parse

import httpx

from ..auth import build_headers, get_base_url
from . import _resp_or_json


def your_function(param1: str, param2: str = "default", raw: bool = False) -> str | httpx.Response:
    """函数描述。"""
    data = {
        "param1": param1,
        "param2": param2,
    }
    resp = httpx.request(
        "POST",
        f"{get_base_url()}/api/path",
        headers=build_headers(),
        content=urllib.parse.urlencode(data),
    )
    return _resp_or_json(resp, raw)
```

**规则：**
- 必须通过 `_resp_or_json()` 返回结果
- `build_headers()` 的 path 参数：有文件路径参数时传入该值，否则传空字符串
- 请求体用 `urllib.parse.urlencode(data)` 编码
- 跳过 URL 中的 `rnd`、`webagent` 等反缓存参数
- 参数名使用可读英文命名
- 需要 `raw` 参数支持原始响应

#### 关于字段映射

如果 API 返回列表数据（数组）且包含缩写字段名，在 `src/zspace/api/fields.py` 中添加映射，
并在 API 函数中格式化。

```python
from .fields import YOUR_API_FIELDS

def _format_your_api(data: list) -> str:
    out = []
    for item in data:
        readable = {}
        for short, val in item.items():
            long_name = YOUR_API_FIELDS.get(short, short)
            if long_name in ("modified_at", "created_at") and isinstance(val, (int, float)) and val:
                readable[long_name] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(val))
            else:
                readable[long_name] = val
        out.append(readable)
    return json.dumps(out, indent=2, ensure_ascii=False)
```

只有响应是列表时才需要逐项字段映射。字典响应由 `_check_resp` 统一处理。


### 第四步：实现 CLI 命令

在 `src/zspace/commands/` 下创建命令文件，然后在 `commands/__init__.py` 注册。

**模板：**

```python
"""xxx 命令 —— 功能描述。"""

from ..api.module import your_function
from .base import Command


class XxxCommand(Command):
    name = "xxx"
    help = "功能描述"

    def register(self, parser):
        parser.add_argument("param1", help="参数描述")
        parser.add_argument("--param2", default="default", help="参数描述")

    def handle(self, args):
        print(your_function(param1=args.param1, param2=args.param2))
```

注册：在 `commands/__init__.py` 中添加 import 和 `_BUILTINS` 类引用。


### 第五步：实现 MCP 工具

在 `src/zspace/mcp/tools/` 下创建工具文件，然后在 `mcp/tools/__init__.py` 注册。

**模板：**

```python
"""xxx 工具 —— AI 调用描述。"""

from ...api.module import your_function
from ..base import McpTool


class XxxTool(McpTool):
    name = "xxx_action"
    description = "AI 理解的描述"
    input_schema = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "参数描述"},
            "param2": {"type": "string", "description": "参数描述", "default": "default"},
        },
        "required": ["param1"],
    }

    def handle(self, arguments: dict) -> str:
        return your_function(param1=arguments["param1"], param2=arguments.get("param2", "default"))
```


### 第六步：测试验证

**只允许使用 `/sata14/my/data/测试文件夹` 作为测试目录。**
如果 curl 中使用的是其他路径，必须替换为此目录再测试。

CLI 测试：
```bash
cd /Users/philip/Documents/code/zspace-cli && ./dev <command> <args>
```

MCP 导入验证：
```bash
cd /Users/philip/Documents/code/zspace-cli && python -c "
import sys; sys.path.insert(0, 'src')
from zspace.mcp.tools import get_all_tools
names = [t.name for t in get_all_tools()]
print(f'Tools: {names}')
assert '<tool_name>' in names
print('OK')
"
```

综合验证（确认没有破坏已有功能）：
```bash
cd /Users/philip/Documents/code/zspace-cli && ./dev list /sata14/my/data/测试文件夹 2>&1 | head -5
```
