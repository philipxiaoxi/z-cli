"""命令层单元测试 —— 覆盖 commands/base 和所有子命令。"""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from zspace.commands import main, register_all
from zspace.commands.base import Command, format_response

# =========================================================
# commands/base.py
# =========================================================

class TestFormatResponse:
    def test_format_json(self, capsys):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = {"key": "value"}
        resp.is_success = True
        with pytest.raises(SystemExit) as exc:
            format_response(resp)
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert json.loads(captured.out) == {"key": "value"}

    def test_format_json_non_success(self, capsys):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = {"error": "fail"}
        resp.is_success = False
        with pytest.raises(SystemExit) as exc:
            format_response(resp)
        assert exc.value.code == 1

    def test_format_non_json_fallback(self, capsys):
        resp = MagicMock(spec=httpx.Response)
        resp.json.side_effect = ValueError("not json")
        resp.text = "plain text"
        resp.is_success = True
        with pytest.raises(SystemExit) as exc:
            format_response(resp)
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert captured.out == "plain text\n"


class TestCommandBase:
    def test_command_is_abstract(self):
        with pytest.raises(TypeError):
            Command()


# =========================================================
# commands/__init__.py
# =========================================================

class TestRegisterAll:
    def test_register_all_creates_subcommands(self):
        parser = __import__("argparse").ArgumentParser(prog="test")
        subparsers = parser.add_subparsers(dest="command", required=True)
        register_all(subparsers)
        known = {a.dest for a in parser._actions if hasattr(a, "choices") and a.choices}
        if known:
            choices = set()
            for action in parser._actions:
                if hasattr(action, "choices") and action.choices:
                    choices.update(action.choices.keys())
        else:
            choices = set(subparsers.choices.keys())
        assert "list" in choices
        assert "ping" in choices
        assert "pool" in choices
        assert "poolname" in choices
        assert "create" in choices
        assert "mkdir" in choices
        assert "remove" in choices
        assert "rename" in choices
        assert "move" in choices
        assert "copy" in choices
        assert "download" in choices
        assert "read" in choices
        assert "recent" in choices
        assert "search" in choices
        assert "mcp" in choices
        assert "skills" in choices
        assert "teamlist" not in choices  # 已合并到 list --team


class TestMain:
    def test_main_routes_to_command(self, capsys):
        with patch(
            "zspace.commands.sys.argv", ["zcli", "ping", "--timeout", "3"]
        ), patch("zspace.commands.ping.ping") as mock_ping:
            mock_ping.return_value = '{"status": "connected"}'
            main()
            captured = capsys.readouterr()
            assert "connected" in captured.out

    def test_main_api_error_exits_with_message(self):
        with patch(
            "zspace.commands.sys.argv", ["zcli", "ping"]
        ), patch("zspace.commands.ping.ping") as mock_ping, pytest.raises(SystemExit):
            from zspace.api import ApiError
            mock_ping.side_effect = ApiError("500", "服务错误")
            main()

    def test_main_no_command_shows_help(self):
        with patch(
            "zspace.commands.sys.argv", ["zcli"]
        ), pytest.raises(SystemExit):
            main()


# =========================================================
# commands/ping.py
# =========================================================

class TestPingCommand:
    def test_handle(self, capsys):
        with patch("zspace.commands.ping.ping") as mock_ping:
            mock_ping.return_value = '{"status": "connected"}'
            from zspace.commands.ping import PingCommand
            cmd = PingCommand()
            args = __import__("argparse").Namespace(timeout=5)
            cmd.handle(args)
            captured = capsys.readouterr()
            assert "connected" in captured.out

    def test_register_adds_argument(self):
        import argparse

        from zspace.commands.ping import PingCommand
        cmd = PingCommand()
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        p = sub.add_parser(cmd.name)
        cmd.register(p)
        args = parser.parse_args(["ping", "--timeout", "10"])
        assert args.timeout == 10


# =========================================================
# commands/list.py
# =========================================================

class TestListCommand:
    def test_handle(self, capsys):
        with patch("zspace.commands.list.list_files") as mock_list:
            mock_list.return_value = '[{"name": "test.txt"}]'
            from zspace.commands.list import ListCommand
            cmd = ListCommand()
            args = __import__("argparse").Namespace(
                path="/sata12/my/data", start="0", num="100",
                sortby="mtime_linux", order="desc",
                with_fields="ext,type", show_hidden="0", dup="0",
                team=False,
            )
            cmd.handle(args)
            captured = capsys.readouterr()
            assert "test.txt" in captured.out

    def test_handle_passes_args(self):
        with patch("zspace.commands.list.list_files") as mock_list:
            from zspace.commands.list import ListCommand
            cmd = ListCommand()
            args = __import__("argparse").Namespace(
                path="/test", start="10", num="50",
                sortby="name", order="asc",
                with_fields="ext", show_hidden="1", dup="1",
                team=False,
            )
            cmd.handle(args)
            mock_list.assert_called_once_with(
                path="/test", start="10", num="50",
                sortby="name", order="asc",
                with_fields="ext", show_hidden="1", dup="1"
            )

    def test_handle_team_mode(self, capsys):
        with patch("zspace.commands.list.list_team_files") as mock_team:
            mock_team.return_value = '[{"name": "团队文件"}]'
            from zspace.commands.list import ListCommand
            cmd = ListCommand()
            args = __import__("argparse").Namespace(
                path="/sata12/public", start="0", num="50",
                team=True,
            )
            cmd.handle(args)
            captured = capsys.readouterr()
            assert "团队文件" in captured.out

    def test_handle_team_default_path(self):
        with patch("zspace.commands.list.list_team_files") as mock_team:
            from zspace.commands.list import ListCommand
            cmd = ListCommand()
            args = __import__("argparse").Namespace(
                path=None, start="0", num="100",
                team=True,
            )
            cmd.handle(args)
            mock_team.assert_called_once_with(
                path="/public", start="0", num="100"
            )

    def test_handle_non_team_no_path(self):
        with patch("zspace.commands.list.list_files") as mock_list:
            from zspace.commands.list import ListCommand
            cmd = ListCommand()
            args = __import__("argparse").Namespace(
                path=None, start="0", num="100",
                sortby="mtime_linux", order="desc",
                with_fields="ext", show_hidden="0", dup="0",
                team=False,
            )
            with pytest.raises(SystemExit):
                cmd.handle(args)


# =========================================================
# commands/pool.py
# =========================================================

class TestPoolCommand:
    def test_handle(self, capsys):
        with patch("zspace.commands.pool.get_pool_info") as mock_pool:
            mock_pool.return_value = '{"pools": []}'
            from zspace.commands.pool import PoolCommand
            cmd = PoolCommand()
            cmd.handle(None)
            captured = capsys.readouterr()
            assert "pools" in captured.out


# =========================================================
# commands/poolname.py
# =========================================================

class TestPoolnameCommand:
    def test_handle(self, capsys):
        with patch("zspace.commands.poolname.get_pool_names") as mock_pn:
            mock_pn.return_value = '{"sata12": "存储"}'
            from zspace.commands.poolname import PoolnameCommand
            cmd = PoolnameCommand()
            cmd.handle(None)
            captured = capsys.readouterr()
            assert "sata12" in captured.out


# =========================================================
# commands/create.py
# =========================================================

class TestCreateCommand:
    def test_handle_with_content(self, capsys):
        with patch("zspace.commands.create.create_file") as mock_create:
            from zspace.commands.create import CreateCommand
            cmd = CreateCommand()
            args = __import__("argparse").Namespace(
                path="/new.txt", rename="0", content="hello"
            )
            cmd.handle(args)
            mock_create.assert_called_once_with(
                path="/new.txt", rename="0", content=b"hello"
            )

    def test_handle_empty_content(self, capsys):
        with patch("zspace.commands.create.create_file") as mock_create:
            from zspace.commands.create import CreateCommand
            cmd = CreateCommand()
            args = __import__("argparse").Namespace(
                path="/empty.txt", rename="1", content=""
            )
            cmd.handle(args)
            mock_create.assert_called_once_with(
                path="/empty.txt", rename="1", content=b""
            )


# =========================================================
# commands/mkdir.py
# =========================================================

class TestMkdirCommand:
    def test_handle(self, capsys):
        with patch("zspace.commands.mkdir.create_folder") as mock_mkdir:
            from zspace.commands.mkdir import MkdirCommand
            cmd = MkdirCommand()
            args = __import__("argparse").Namespace(
                parent="/sata12/my/data", name="newdir", rename="0"
            )
            cmd.handle(args)
            mock_mkdir.assert_called_once_with(
                parent="/sata12/my/data", name="newdir", rename="0"
            )


# =========================================================
# commands/remove.py
# =========================================================

class TestRemoveCommand:
    def test_handle_single(self, capsys):
        with patch("zspace.commands.remove.delete_item") as mock_del:
            from zspace.commands.remove import RemoveCommand
            cmd = RemoveCommand()
            args = __import__("argparse").Namespace(
                paths="/a.txt", show_hidden=False
            )
            cmd.handle(args)
            mock_del.assert_called_once_with(paths="/a.txt", show_hidden=False)

    def test_handle_multiple(self, capsys):
        with patch("zspace.commands.remove.delete_item") as mock_del:
            from zspace.commands.remove import RemoveCommand
            cmd = RemoveCommand()
            args = __import__("argparse").Namespace(
                paths="/a.txt, /b.txt", show_hidden=True
            )
            cmd.handle(args)
            mock_del.assert_called_once_with(
                paths=["/a.txt", "/b.txt"], show_hidden=True
            )


# =========================================================
# commands/rename.py
# =========================================================

class TestRenameCommand:
    def test_handle(self, capsys):
        with patch("zspace.commands.rename.rename_item") as mock_ren:
            from zspace.commands.rename import RenameCommand
            cmd = RenameCommand()
            args = __import__("argparse").Namespace(
                path="/data/old.txt", newname="new.txt"
            )
            cmd.handle(args)
            mock_ren.assert_called_once_with(
                path="/data/old.txt", newname="new.txt"
            )


# =========================================================
# commands/move.py
# =========================================================

class TestMoveCommand:
    def test_handle_single(self, capsys):
        with patch("zspace.commands.move.move_item") as mock_move:
            from zspace.commands.move import MoveCommand
            cmd = MoveCommand()
            args = __import__("argparse").Namespace(
                paths="/a.txt", to="/backup", rename="0"
            )
            cmd.handle(args)
            mock_move.assert_called_once_with(
                paths="/a.txt", to="/backup", rename="0"
            )

    def test_handle_multiple(self, capsys):
        with patch("zspace.commands.move.move_item") as mock_move:
            from zspace.commands.move import MoveCommand
            cmd = MoveCommand()
            args = __import__("argparse").Namespace(
                paths="/a.txt, /b.txt", to="/backup", rename="1"
            )
            cmd.handle(args)
            mock_move.assert_called_once_with(
                paths=["/a.txt", "/b.txt"], to="/backup", rename="1"
            )


# =========================================================
# commands/copy.py
# =========================================================

class TestCopyCommand:
    def test_handle_single(self, capsys):
        with patch("zspace.commands.copy.copy_item") as mock_copy:
            from zspace.commands.copy import CopyCommand
            cmd = CopyCommand()
            args = __import__("argparse").Namespace(
                paths="/a.txt", to="/backup", rename="0"
            )
            cmd.handle(args)
            mock_copy.assert_called_once_with(
                paths="/a.txt", to="/backup", rename="0"
            )

    def test_handle_multiple(self, capsys):
        with patch("zspace.commands.copy.copy_item") as mock_copy:
            from zspace.commands.copy import CopyCommand
            cmd = CopyCommand()
            args = __import__("argparse").Namespace(
                paths="/a.txt, /b.txt", to="/backup", rename="1"
            )
            cmd.handle(args)
            mock_copy.assert_called_once_with(
                paths=["/a.txt", "/b.txt"], to="/backup", rename="1"
            )


# =========================================================
# commands/download.py
# =========================================================

class TestDownloadCommand:
    def test_handle(self, capsys, tmp_path):
        with patch("zspace.commands.download.download_file") as mock_dl:
            mock_dl.return_value = b"binary content"
            from zspace.commands.download import DownloadCommand
            cmd = DownloadCommand()
            args = __import__("argparse").Namespace(
                path="/sata12/my/data/file.txt", output_dir=str(tmp_path)
            )
            cmd.handle(args)
            captured = capsys.readouterr()
            assert "file.txt" in captured.out
            assert (tmp_path / "file.txt").read_bytes() == b"binary content"


# =========================================================
# commands/read.py
# =========================================================

class TestReadCommand:
    def test_handle(self, capsys):
        with patch("zspace.commands.read.read_file") as mock_read:
            mock_read.return_value = "file content"
            from zspace.commands.read import ReadCommand
            cmd = ReadCommand()
            args = __import__("argparse").Namespace(
                path="/test.txt", remote_port="8050"
            )
            cmd.handle(args)
            captured = capsys.readouterr()
            assert "file content" in captured.out

    def test_handle_passes_args(self):
        with patch("zspace.commands.read.read_file") as mock_read:
            from zspace.commands.read import ReadCommand
            cmd = ReadCommand()
            args = __import__("argparse").Namespace(
                path="/test.txt", remote_port="8080"
            )
            cmd.handle(args)
            mock_read.assert_called_once_with(
                path="/test.txt", remote_port="8080"
            )


# =========================================================
# commands/recent.py
# =========================================================

class TestRecentCommand:
    def test_handle(self, capsys):
        with patch("zspace.commands.recent.list_recent_files") as mock_recent:
            mock_recent.return_value = '[{"name": "recent.txt"}]'
            from zspace.commands.recent import RecentCommand
            cmd = RecentCommand()
            args = __import__("argparse").Namespace(
                start="0", num="50", scope="1", show_hidden="0"
            )
            cmd.handle(args)
            captured = capsys.readouterr()
            assert "recent.txt" in captured.out


# =========================================================
# commands/search.py
# =========================================================

class TestSearchCommand:
    def test_handle(self, capsys):
        with patch("zspace.commands.search.search_files") as mock_search:
            mock_search.return_value = '[{"name": "found.txt"}]'
            from zspace.commands.search import SearchCommand
            cmd = SearchCommand()
            args = __import__("argparse").Namespace(
                name="test", path="/sata12/my/data",
                order_by="0", ftype="", is_dir="",
                min_size="0", max_size="0",
                start="0", num="30",
                shared_only="0", show_hidden="0"
            )
            cmd.handle(args)
            captured = capsys.readouterr()
            assert "found.txt" in captured.out

    def test_handle_passes_args(self):
        with patch("zspace.commands.search.search_files") as mock_search:
            from zspace.commands.search import SearchCommand
            cmd = SearchCommand()
            args = __import__("argparse").Namespace(
                name="doc", path="/data",
                order_by="1", ftype="txt", is_dir="0",
                min_size="100", max_size="10000",
                start="0", num="50",
                shared_only="0", show_hidden="0"
            )
            cmd.handle(args)
            mock_search.assert_called_once_with(
                name="doc", file_path="/data",
                order_by="1", ftype="txt", is_dir="0",
                min_size="100", max_size="10000",
                start="0", num="50",
                shared_only="0", show_hidden="0"
            )


# =========================================================
# commands/skills.py
# =========================================================

class TestSkillsCommand:
    def test_register_creates_subparsers(self):
        import argparse

        from zspace.commands.skills import SkillsCommand
        cmd = SkillsCommand()
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers()
        p = sub.add_parser(cmd.name)
        cmd.register(p)
        args = parser.parse_args(["skills", "install", "test-skill", "--agent", "opencode"])
        assert args.skills_action == "install"
        assert args.name == "test-skill"
        assert args.agents == ["opencode"]

    def test_install_missing_skill(self, capsys):
        from zspace.commands.skills import SkillsCommand
        cmd = SkillsCommand()
        args = __import__("argparse").Namespace(
            skills_action="install", name="nonexistent", agents=["opencode"]
        )
        with pytest.raises(SystemExit):
            cmd.handle(args)
        captured = capsys.readouterr()
        assert "不存在" in captured.err

    def test_uninstall_nonexistent(self, capsys):
        from zspace.commands.skills import SkillsCommand
        cmd = SkillsCommand()
        args = __import__("argparse").Namespace(
            skills_action="uninstall", name="nonexistent", agents=["opencode"]
        )
        cmd.handle(args)
        captured = capsys.readouterr()
        assert "不存在" in captured.out

    def test_install_success(self, capsys):
        from zspace.commands.skills import SkillsCommand
        with patch("zspace.commands.skills.shutil.copytree"), \
                patch("zspace.commands.skills.Path.is_dir", return_value=True), \
                patch("zspace.commands.skills.Path.__truediv__") as mock_div:
            mock_div.return_value = __import__("pathlib").Path("/tmp/fake-skill")
            cmd = SkillsCommand()
            args = __import__("argparse").Namespace(
                skills_action="install", name="test-skill",
                agents=["opencode", "claude"]
            )
            cmd.handle(args)
            captured = capsys.readouterr()
            assert "已安装" in captured.out

    def test_uninstall_success(self, capsys, tmp_path):
        from zspace.commands.skills import SkillsCommand
        with patch("zspace.commands.skills.Path.exists") as mock_exists, \
                patch("zspace.commands.skills.shutil.rmtree"):
            mock_exists.return_value = True
            cmd = SkillsCommand()
            args = __import__("argparse").Namespace(
                skills_action="uninstall", name="test-skill",
                agents=["opencode", "claude"]
            )
            cmd.handle(args)
            captured = capsys.readouterr()
            assert "已从" in captured.out



