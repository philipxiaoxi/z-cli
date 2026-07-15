"""API 层单元测试 —— 覆盖 api/__init__、file、ping、pool、user、fields 模块。"""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest


@pytest.fixture(autouse=True)
def _mock_auth():
    """所有 API 测试自动 mock 认证模块，避免读取本地 vuex.json。

    除非测试自行覆盖（如 TestPing 系列有独立的 mock）。
    """
    with patch("zspace.auth._load_vuex") as mock_load:
        mock_load.return_value = {"app": {"localPort": 13579}, "user": {"token": "test"}}
        yield


from zspace.api import ApiError, _check_resp, _resp_or_json
from zspace.api.fields import FILE_LIST
from zspace.api.file import (
    _format_list,
    copy_item,
    create_file,
    create_folder,
    delete_item,
    download_file,
    list_files,
    list_recent_files,
    move_item,
    read_file,
    rename_item,
    search_files,
)
from zspace.api.ping import ping
from zspace.api.pool import get_pool_info
from zspace.api.user import get_pool_names


# =========================================================
# api/__init__.py
# =========================================================

class TestApiError:
    def test_error_str(self):
        err = ApiError("400", "bad request", {"code": "400"})
        assert err.code == "400"
        assert err.msg == "bad request"
        assert err.data == {"code": "400"}
        assert str(err) == "[400] bad request"

    def test_error_without_data(self):
        err = ApiError("500", "server error")
        assert err.data is None
        assert str(err) == "[500] server error"


class TestCheckResp:
    def test_success_code(self):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = {"code": "200", "data": "ok"}
        assert _check_resp(resp) == {"code": "200", "data": "ok"}

    def test_missing_code(self):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = {"data": "ok"}
        assert _check_resp(resp) == {"data": "ok"}

    def test_error_code(self):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = {"code": "400", "msg": "invalid"}
        with pytest.raises(ApiError) as exc:
            _check_resp(resp)
        assert exc.value.code == "400"
        assert exc.value.msg == "invalid"

    def test_error_code_without_msg(self):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = {"code": "500"}
        with pytest.raises(ApiError) as exc:
            _check_resp(resp)
        assert exc.value.code == "500"
        assert exc.value.msg == ""

    def test_list_response(self):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = [{"n": "file.txt"}]
        assert _check_resp(resp) == [{"n": "file.txt"}]


class TestRespOrJson:
    def test_raw_returns_response(self):
        resp = MagicMock(spec=httpx.Response)
        result = _resp_or_json(resp, raw=True)
        assert result is resp

    def test_formatted_json(self):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = {"code": "200", "data": "ok"}
        result = _resp_or_json(resp, raw=False)
        parsed = json.loads(result)
        assert parsed == {"code": "200", "data": "ok"}

    def test_formatted_list_json(self):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = [{"n": "file.txt"}]
        result = _resp_or_json(resp, raw=False)
        parsed = json.loads(result)
        assert parsed == [{"n": "file.txt"}]

    def test_error_response_formatted(self):
        resp = MagicMock(spec=httpx.Response)
        resp.json.return_value = {"code": "500", "msg": "fail"}
        with pytest.raises(ApiError):
            _resp_or_json(resp, raw=False)


# =========================================================
# api/fields.py
# =========================================================

class TestFileListFields:
    def test_has_expected_keys(self):
        assert "n" in FILE_LIST
        assert "di" in FILE_LIST
        assert "s" in FILE_LIST
        assert "mt" in FILE_LIST
        assert "ct" in FILE_LIST

    def test_field_names_are_readable(self):
        assert FILE_LIST["n"] == "name"
        assert FILE_LIST["di"] == "is_dir"
        assert FILE_LIST["s"] == "size_bytes"
        assert FILE_LIST["mt"] == "modified_at"
        assert FILE_LIST["ct"] == "created_at"

    def test_all_mappings_are_strings(self):
        for k, v in FILE_LIST.items():
            assert isinstance(k, str)
            assert isinstance(v, str)


# =========================================================
# api/file.py — _format_list
# =========================================================

class TestFormatList:
    def test_field_mapping(self):
        data = [{"n": "test.txt", "di": "0", "s": 1024}]
        result = json.loads(_format_list(data))
        assert result[0]["name"] == "test.txt"
        assert result[0]["is_dir"] == "0"
        assert result[0]["size_bytes"] == 1024
        assert "n" not in result[0]

    def test_timestamp_conversion(self):
        data = [{"mt": 1700000000, "ct": 1700000000}]
        result = json.loads(_format_list(data))
        import time
        expected = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(1700000000))
        assert result[0]["modified_at"] == expected
        assert result[0]["created_at"] == expected

    def test_zero_timestamp_not_converted(self):
        data = [{"mt": 0, "ct": None}]
        result = json.loads(_format_list(data))
        assert result[0]["modified_at"] == 0
        assert result[0]["created_at"] is None

    def test_unknown_field_preserved(self):
        data = [{"unknown_field": "value"}]
        result = json.loads(_format_list(data))
        assert result[0]["unknown_field"] == "value"

    def test_empty_list(self):
        assert _format_list([]) == "[]"


# =========================================================
# api/file.py — API functions
# =========================================================

class MockResponse:
    """Helper to create httpx.Response-like objects without real HTTP."""

    def __init__(self, json_data=None, status_code=200, text=""):
        self._json_data = json_data
        self.status_code = status_code
        if isinstance(text, bytes):
            self.content = text
            self.text = text.decode("utf-8", errors="replace")
        else:
            self.text = text or json.dumps(json_data, ensure_ascii=False)
            self.content = self.text.encode("utf-8")
        self.is_success = 200 <= status_code < 300
        self.headers = {}

    def json(self):
        return self._json_data


class TestListFiles:
    def test_list_files_raw(self):
        mock_resp = MockResponse([{"n": "a.txt"}])
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = list_files(path="/sata12/my/data", raw=True)
        assert result is mock_resp
        mock_client.request.assert_called_once()

    def test_list_files_formatted(self):
        mock_resp = MockResponse([{"n": "a.txt", "mt": 1700000000}])
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = list_files(path="/sata12/my/data")
        parsed = json.loads(result)
        assert parsed[0]["name"] == "a.txt"

    def test_list_files_dict_response(self):
        mock_resp = MockResponse({"code": "200", "msg": "ok"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = list_files(path="/sata12/my/data")
        parsed = json.loads(result)
        assert parsed["code"] == "200"


class TestDeleteItem:
    def test_delete_single_string(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            delete_item(paths="/sata12/my/data/a.txt", raw=False)

    def test_delete_list(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            delete_item(paths=["/a.txt", "/b.txt"], raw=True)
        assert mock_client.request.call_args[1]["content"] is not None


class TestRenameItem:
    def test_rename(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            rename_item(path="/sata12/my/data/old.txt", newname="new.txt")

    def test_rename_raw(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = rename_item(path="/old.txt", newname="new.txt", raw=True)
            assert result is mock_resp


class TestMoveItem:
    def test_move_single(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            move_item(paths="/sata12/my/data/a.txt", to="/sata12/my/backup")

    def test_move_list(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            move_item(paths=["/a.txt", "/b.txt"], to="/backup", rename="1", raw=True)

    def test_move_empty_paths(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            move_item(paths=[], to="/backup")

    def test_move_with_rename(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = move_item(paths="/a.txt", to="/b.txt", rename="1", raw=True)
            assert result is mock_resp


class TestCopyItem:
    def test_copy_single(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            copy_item(paths="/sata12/my/data/a.txt", to="/sata12/my/backup")

    def test_copy_list(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            copy_item(paths=["/a.txt", "/b.txt"], to="/backup", rename="1", raw=True)

    def test_copy_raw(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = copy_item(paths="/a.txt", to="/b.txt", raw=True)
            assert result is mock_resp


class TestListRecentFiles:
    def test_recent_files_defaults(self):
        mock_resp = MockResponse([{"n": "recent.txt"}])
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = list_recent_files()
        parsed = json.loads(result)
        assert parsed[0]["name"] == "recent.txt"

    def test_recent_files_raw(self):
        mock_resp = MockResponse([{"n": "recent.txt"}])
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = list_recent_files(raw=True)
            assert result is mock_resp

    def test_recent_files_dict_response(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = list_recent_files()
            parsed = json.loads(result)
            assert parsed["code"] == "200"


class TestCreateFile:
    def test_create_file_default(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            create_file(path="/sata12/my/data/new.txt")

    def test_create_file_with_content(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            create_file(path="/new.txt", content=b"hello world")

    def test_create_file_raw(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = create_file(path="/new.txt", raw=True)
            assert result is mock_resp

    def test_create_file_with_rename(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            create_file(path="/new.txt", rename="1")


class TestCreateFolder:
    def test_create_folder(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            create_folder(parent="/sata12/my/data", name="newdir")

    def test_create_folder_with_rename(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            create_folder(parent="/data", name="newdir", rename="1")

    def test_create_folder_raw(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = create_folder(parent="/data", name="newdir", raw=True)
            assert result is mock_resp


class TestReadFile:
    def test_read_text_file(self):
        mock_resp = MockResponse({}, status_code=200, text="file content")
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = read_file(path="/sata12/my/data/test.txt")
        assert result == "file content"

    def test_read_raw(self):
        mock_resp = MockResponse({}, status_code=200, text="raw content")
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = read_file(path="/test.txt", raw=True)
            assert result is mock_resp

    def test_read_error_status(self):
        mock_resp = MockResponse({}, status_code=404)
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = read_file(path="/test.txt")
            assert "错误" in result
            assert "404" in result

    def test_read_non_text_extension(self):
        mock_resp = MockResponse({}, status_code=200, text=b"binary data")
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = read_file(path="/test.bin")
            assert "错误" in result
            assert ".bin" in result

    def test_read_unknown_extension_rejected(self):
        mock_resp = MockResponse({}, status_code=200, text="content")
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = read_file(path="/test.unknown_ext")
        assert "错误" in result

    def test_read_file_no_extension(self):
        mock_resp = MockResponse({}, status_code=200, text="content")
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = read_file(path="/README")
            assert result == "content"


class TestSearchFiles:
    def test_search_defaults(self):
        mock_resp = MockResponse([{"n": "found.txt"}])
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = search_files(name="test", file_path="/sata12/my/data")
        parsed = json.loads(result)
        assert parsed[0]["name"] == "found.txt"

    def test_search_raw(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = search_files(name="test", file_path="/data", raw=True)
            assert result is mock_resp

    def test_search_dict_response(self):
        mock_resp = MockResponse({"code": "200", "msg": "ok"})
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = search_files(name="test", file_path="/data")
            parsed = json.loads(result)
            assert parsed["code"] == "200"

    def test_search_with_filters(self):
        mock_resp = MockResponse([{"n": "doc.txt"}])
        with patch("zspace.api.file._client") as mock_client:
            mock_client.request.return_value = mock_resp
            search_files(
                name="doc",
                file_path="/data",
                ftype="txt",
                is_dir="0",
                min_size="100",
                max_size="10000",
                order_by="1",
            )


class TestDownloadFile:
    def test_download_success(self):
        mock_resp = httpx.Response(status_code=200, content=b"binary data")
        with patch("zspace.api.file._client") as mock_client, \
                patch("zspace.api.file.read_file", return_value=mock_resp):
            result = download_file(path="/sata12/my/data/file.bin")
        assert result == b"binary data"

    def test_download_error(self):
        mock_resp = httpx.Response(status_code=404)
        with patch("zspace.api.file._client") as mock_client, \
                patch("zspace.api.file.read_file", return_value=mock_resp):
            with pytest.raises(ApiError) as exc:
                download_file(path="/missing.bin")
            assert "404" in str(exc.value)


# =========================================================
# api/ping.py
# =========================================================

class TestPing:
    def test_success(self):
        with patch("zspace.api.ping.get_base_url") as mock_url, \
                patch("zspace.api.ping.httpx.get") as mock_get:
            mock_url.return_value = "http://127.0.0.1:13579"
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp
            result = json.loads(ping())
        assert result["status"] == "connected"
        assert result["status_code"] == 200
        assert result["host"] == "http://127.0.0.1:13579"

    def test_connect_error(self):
        with patch("zspace.api.ping.get_base_url") as mock_url, \
                patch("zspace.api.ping.httpx.get") as mock_get:
            mock_url.return_value = "http://127.0.0.1:13579"
            mock_get.side_effect = httpx.ConnectError("connection refused")
            result = json.loads(ping())
        assert result["status"] == "unreachable"
        assert "无法连接到" in result["error"]

    def test_timeout(self):
        with patch("zspace.api.ping.get_base_url") as mock_url, \
                patch("zspace.api.ping.httpx.get") as mock_get:
            mock_url.return_value = "http://127.0.0.1:13579"
            mock_get.side_effect = httpx.TimeoutException("timeout")
            result = json.loads(ping(timeout=3))
        assert result["status"] == "timeout"
        assert "超时" in result["error"]

    def test_generic_exception(self):
        with patch("zspace.api.ping.get_base_url") as mock_url, \
                patch("zspace.api.ping.httpx.get") as mock_get:
            mock_url.return_value = "http://127.0.0.1:13579"
            mock_get.side_effect = RuntimeError("unexpected")
            result = json.loads(ping())
        assert result["status"] == "error"
        assert "unexpected" in result["error"]

    def test_has_timestamp_and_host(self):
        with patch("zspace.api.ping.get_base_url") as mock_url, \
                patch("zspace.api.ping.httpx.get") as mock_get:
            mock_url.return_value = "http://192.168.1.1:8888"
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp
            result = json.loads(ping())
        assert result["host"] == "http://192.168.1.1:8888"
        assert isinstance(result["timestamp"], int)


# =========================================================
# api/pool.py
# =========================================================

class TestGetPoolInfo:
    def test_pool_info(self):
        mock_resp = MockResponse({"code": "200", "data": [{"name": "sata12"}]})
        with patch("zspace.api.pool._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = get_pool_info()
        parsed = json.loads(result)
        assert parsed["code"] == "200"

    def test_pool_info_raw(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.pool._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = get_pool_info(raw=True)
            assert result is mock_resp


# =========================================================
# api/user.py
# =========================================================

class TestGetPoolNames:
    def test_pool_names(self):
        mock_data = {
            "code": "200",
            "data": {
                "list": [
                    {
                        "pn": [
                            {"k": "sata12", "n": "日立高速"},
                            {"k": "sata14", "n": "西数存储"},
                        ]
                    }
                ]
            },
        }
        mock_resp = MockResponse(mock_data)
        with patch("zspace.api.user._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = get_pool_names()
        parsed = json.loads(result)
        assert parsed == {"sata12": "日立高速", "sata14": "西数存储"}

    def test_pool_names_raw(self):
        mock_resp = MockResponse({"code": "200"})
        with patch("zspace.api.user._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = get_pool_names(raw=True)
            assert result is mock_resp

    def test_pool_names_empty_list(self):
        mock_data = {"code": "200", "data": {"list": []}}
        mock_resp = MockResponse(mock_data)
        with patch("zspace.api.user._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = get_pool_names()
            assert json.loads(result) == {}

    def test_pool_names_no_list_key(self):
        mock_data = {"code": "200", "data": {}}
        mock_resp = MockResponse(mock_data)
        with patch("zspace.api.user._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = get_pool_names()
            assert json.loads(result) == {}

    def test_pool_names_multiple_users_first_wins(self):
        mock_data = {
            "code": "200",
            "data": {
                "list": [
                    {"pn": [{"k": "pool1", "n": "First"}]},
                    {"pn": [{"k": "pool2", "n": "Second"}]},
                ]
            },
        }
        mock_resp = MockResponse(mock_data)
        with patch("zspace.api.user._client") as mock_client:
            mock_client.request.return_value = mock_resp
            result = get_pool_names()
            assert json.loads(result) == {"pool1": "First"}
