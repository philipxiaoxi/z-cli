# Python 3.14 macOS UF_HIDDEN .pth 文件跳过问题

## 问题

Python 3.14 的 `site.addpackage()` 新增了对 `UF_HIDDEN` stat 标志的检查。当 `site-packages/` 目录下的 `.pth` 文件被 macOS 标记为隐藏时，Python 会直接跳过该文件，导致路径未加入 `sys.path`，模块无法导入。

## 症状

```
$ zcli
Traceback (most recent call last):
  File ".../zcli", line 3, in <module>
    from zspace.commands import main
ModuleNotFoundError: No module named 'zspace'
```

Python verbose 模式下可见：

```
Skipping hidden .pth file: '.../site-packages/__editable__.z_cli-0.1.0.pth'
```

## 根因

setuptools 的可编辑安装（`pip install -e .`）依赖 `__editable__.<package>-<version>.pth` 文件将源码目录加入 `sys.path`。

在 macOS 上，当文件被赋予 `com.apple.provenance` 扩展属性时，系统会自动设置 `UF_HIDDEN` 文件标志。Python 3.14 `site.addpackage()` 中新增了以下检查（CPython 3.14 新增）：

```python
if ((getattr(st, 'st_flags', 0) & stat.UF_HIDDEN) or
    (getattr(st, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_HIDDEN)):
    _trace(f"Skipping hidden .pth file: {fullname!r}")
    return
```

## 修复

### 临时修复（单文件）

```bash
xattr -c .venv/lib/python3.14/site-packages/__editable__.z_cli-0.1.0.pth
chflags 0 .venv/lib/python3.14/site-packages/__editable__.z_cli-0.1.0.pth
```

先清除 `com.apple.provenance` 扩展属性，再清除文件标志。

### 推荐方案：使用 pipx 全局安装

pipx 创建的独立虚拟环境中同样会生成 `__editable__` 文件，但通常不会被 macOS 自动标记隐藏标志。pipx 安装后直接在 opencode 中引用 `~/.local/bin/zcli` 即可。

```bash
pipx install -e /path/to/zspace-cli
```

## 受影响的环境

- Python 3.14+（首次引入 `UF_HIDDEN` 检查）
- macOS（使用 `st_flags` 和 `UF_HIDDEN` 标志的系统）
- 通过 `pip install -e .` 可编辑安装的 Python 包

## 相关链接

- CPython issue: https://github.com/python/cpython/issues/114808（在 site.addpackage 中跳过隐藏的 .pth 文件）
- PEP 668: 外部管理的 Python 环境
