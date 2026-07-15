"""MCP 层单元测试 —— 覆盖 mcp/base、mcp/__init__、mcp/tools。"""

from unittest.mock import MagicMock, patch

import mcp.types as types
import pytest

from zspace.mcp.base import McpTool
from zspace.mcp.tools import get_all_tools
from zspace.mcp.tools.copy import CopyTool
from zspace.mcp.tools.create import CreateFileTool
from zspace.mcp.tools.list import ListFilesTool
from zspace.mcp.tools.mkdir import MkdirTool
from zspace.mcp.tools.move import MoveTool
from zspace.mcp.tools.ping import PingTool
from zspace.mcp.tools.pool import PoolTool
from zspace.mcp.tools.poolname import PoolnameTool
from zspace.mcp.tools.read import ReadFileTool
from zspace.mcp.tools.recent import ListRecentFilesTool
from zspace.mcp.tools.remove import RemoveTool
from zspace.mcp.tools.rename import RenameTool
from zspace.mcp.tools.search import SearchTool


# =========================================================
# mcp/base.py
# =========================================================

class TestMcpTool:
    def test_to_mcp_tool(self):
        tool = PingTool()
        mcp_tool = tool.to_mcp_tool()
        assert isinstance(mcp_tool, types.Tool)
        assert mcp_tool.name == "check_connectivity"
        assert mcp_tool.description
        assert "type" in mcp_tool.inputSchema
        assert "properties" in mcp_tool.inputSchema

    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            McpTool()


# =========================================================
# mcp/__init__.py
# =========================================================

class TestMcpServer:
    def test_list_tools_returns_all(self):
        with patch("zspace.mcp.get_all_tools") as mock_get:
            mock_get.return_value = [PingTool(), PoolTool()]
            from zspace.mcp import list_tools
            import anyio
            tools = anyio.run(list_tools)
            names = {t.name for t in tools}
            assert "check_connectivity" in names
            assert "get_pool_info" in names

    def test_call_tool_routes_correctly(self):
        with patch("zspace.mcp.get_all_tools") as mock_get:
            tool = PingTool()
            mock_get.return_value = [tool]
            from zspace.mcp import call_tool
            import anyio
            result = anyio.run(call_tool, "check_connectivity", {"timeout": 3})
            assert len(result) == 1
            assert result[0].type == "text"

    def test_call_tool_unknown_raises(self):
        with patch("zspace.mcp.get_all_tools") as mock_get:
            mock_get.return_value = [PingTool()]
            from zspace.mcp import call_tool
            import anyio
            with pytest.raises(ValueError) as exc:
                anyio.run(call_tool, "nonexistent", {})
            assert "未知工具" in str(exc.value)


# =========================================================
# mcp/tools/__init__.py
# =========================================================

class TestGetAllTools:
    def test_returns_all_tool_instances(self):
        tools = get_all_tools()
        assert len(tools) >= 13  # 所有工具
        names = {t.name for t in tools}
        assert "check_connectivity" in names
        assert "list_files" in names
        assert "create_file" in names
        assert "create_folder" in names
        assert "copy_item" in names
        assert "move_item" in names
        assert "delete_item" in names
        assert "rename_item" in names
        assert "read_file" in names
        assert "list_recent_files" in names
        assert "search_files" in names
        assert "get_pool_info" in names
        assert "get_pool_names" in names

    def test_all_have_input_schema(self):
        for tool in get_all_tools():
            assert tool.input_schema, f"{tool.name} missing input_schema"


# =========================================================
# mcp/tools/ping.py
# =========================================================

class TestPingTool:
    def test_name_and_schema(self):
        tool = PingTool()
        assert tool.name == "check_connectivity"
        assert "timeout" in tool.input_schema["properties"]

    def test_handle(self):
        with patch("zspace.mcp.tools.ping.ping") as mock_ping:
            mock_ping.return_value = '{"status": "ok"}'
            tool = PingTool()
            result = tool.handle({"timeout": 5})
            assert "ok" in result
            mock_ping.assert_called_once_with(timeout=5)

    def test_handle_default_timeout(self):
        with patch("zspace.mcp.tools.ping.ping") as mock_ping:
            tool = PingTool()
            tool.handle({})
            mock_ping.assert_called_once_with(timeout=5)


# =========================================================
# mcp/tools/list.py
# =========================================================

class TestListFilesTool:
    def test_name_and_schema(self):
        tool = ListFilesTool()
        assert tool.name == "list_files"
        assert "path" in tool.input_schema["properties"]
        assert tool.input_schema["required"] == ["path"]

    def test_handle(self):
        with patch("zspace.mcp.tools.list.list_files") as mock_list:
            tool = ListFilesTool()
            tool.handle({"path": "/sata12/my/data"})
            mock_list.assert_called_once_with(
                path="/sata12/my/data", start="0", num="100",
                sortby="mtime_linux", order="desc", show_hidden="0"
            )


# =========================================================
# mcp/tools/create.py
# =========================================================

class TestCreateFileTool:
    def test_handle_with_content(self):
        with patch("zspace.mcp.tools.create.create_file") as mock_create:
            tool = CreateFileTool()
            tool.handle({"path": "/new.txt", "rename": "1", "content": "hello"})
            mock_create.assert_called_once_with(
                path="/new.txt", rename="1", content=b"hello"
            )

    def test_handle_without_content(self):
        with patch("zspace.mcp.tools.create.create_file") as mock_create:
            tool = CreateFileTool()
            tool.handle({"path": "/new.txt"})
            mock_create.assert_called_once_with(
                path="/new.txt", rename="0", content=b""
            )


# =========================================================
# mcp/tools/mkdir.py
# =========================================================

class TestMkdirTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.mkdir.create_folder") as mock_mkdir:
            tool = MkdirTool()
            tool.handle({"parent": "/data", "name": "newdir"})
            mock_mkdir.assert_called_once_with(
                parent="/data", name="newdir", rename="0"
            )


# =========================================================
# mcp/tools/copy.py
# =========================================================

class TestCopyTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.copy.copy_item") as mock_copy:
            tool = CopyTool()
            tool.handle({"paths": ["/a.txt"], "to": "/backup"})
            mock_copy.assert_called_once_with(
                paths=["/a.txt"], to="/backup", rename="0"
            )


# =========================================================
# mcp/tools/move.py
# =========================================================

class TestMoveTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.move.move_item") as mock_move:
            tool = MoveTool()
            tool.handle({"paths": ["/a.txt"], "to": "/backup", "rename": "1"})
            mock_move.assert_called_once_with(
                paths=["/a.txt"], to="/backup", rename="1"
            )


# =========================================================
# mcp/tools/remove.py
# =========================================================

class TestRemoveTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.remove.delete_item") as mock_del:
            tool = RemoveTool()
            tool.handle({"paths": ["/a.txt"], "show_hidden": True})
            mock_del.assert_called_once_with(
                paths=["/a.txt"], show_hidden=True
            )

    def test_handle_defaults(self):
        with patch("zspace.mcp.tools.remove.delete_item") as mock_del:
            tool = RemoveTool()
            tool.handle({"paths": ["/a.txt"]})
            mock_del.assert_called_once_with(
                paths=["/a.txt"], show_hidden=False
            )


# =========================================================
# mcp/tools/rename.py
# =========================================================

class TestRenameTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.rename.rename_item") as mock_ren:
            tool = RenameTool()
            tool.handle({"path": "/old.txt", "newname": "new.txt"})
            mock_ren.assert_called_once_with(
                path="/old.txt", newname="new.txt"
            )


# =========================================================
# mcp/tools/read.py
# =========================================================

class TestReadFileTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.read.read_file") as mock_read:
            tool = ReadFileTool()
            tool.handle({"path": "/test.txt"})
            mock_read.assert_called_once_with(path="/test.txt")


# =========================================================
# mcp/tools/recent.py
# =========================================================

class TestListRecentFilesTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.recent.list_recent_files") as mock_recent:
            tool = ListRecentFilesTool()
            tool.handle({"num": "50"})
            mock_recent.assert_called_once_with(
                start="0", num="50", scope="1", show_hidden="0"
            )

    def test_handle_defaults(self):
        with patch("zspace.mcp.tools.recent.list_recent_files") as mock_recent:
            tool = ListRecentFilesTool()
            tool.handle({})
            mock_recent.assert_called_once_with(
                start="0", num="100", scope="1", show_hidden="0"
            )


# =========================================================
# mcp/tools/search.py
# =========================================================

class TestSearchTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.search.search_files") as mock_search:
            tool = SearchTool()
            tool.handle({"name": "test", "file_path": "/data", "num": "50"})
            mock_search.assert_called_once_with(
                name="test", file_path="/data", order_by="0",
                ftype="", is_dir="", min_size="0", max_size="0",
                start="0", num="50", shared_only="0", show_hidden="0"
            )


# =========================================================
# mcp/tools/pool.py
# =========================================================

class TestPoolTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.pool.get_pool_info") as mock_pool:
            tool = PoolTool()
            tool.handle({})
            mock_pool.assert_called_once()


# =========================================================
# mcp/tools/poolname.py
# =========================================================

class TestPoolnameTool:
    def test_handle(self):
        with patch("zspace.mcp.tools.poolname.get_pool_names") as mock_pn:
            tool = PoolnameTool()
            tool.handle({})
            mock_pn.assert_called_once()
