"""认证模块测试。"""

from unittest.mock import patch

import pytest

from zspace.auth import (
    AuthError,
    _load_vuex,
    build_cookie_header,
    build_cookies,
    build_headers,
    get_base_url,
)


class TestGetBaseUrl:
    def test_default_port(self):
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = {"app": {"localPort": 13579}}
            assert get_base_url() == "http://127.0.0.1:13579"

    def test_environment_variable(self, monkeypatch):
        monkeypatch.setenv("ZSPACE_HOST", "http://192.168.1.100:8888")
        assert get_base_url() == "http://192.168.1.100:8888"

    def test_env_variable_trailing_slash(self, monkeypatch):
        monkeypatch.setenv("ZSPACE_HOST", "http://192.168.1.100:8888/")
        assert get_base_url() == "http://192.168.1.100:8888"

    def test_missing_port_from_vuex(self):
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = {"app": {}}
            assert get_base_url() == "http://127.0.0.1:13579"

    def test_empty_app_in_vuex(self):
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = {}
            assert get_base_url() == "http://127.0.0.1:13579"


class TestLoadVuex:
    def test_caching(self):
        import zspace.auth
        zspace.auth._vuex_cache = None
        mock_data = '{"state": {"app": {"localPort": 12345}}}'
        with patch("zspace.auth.ZSPACE_DIR") as mock_zspace, \
                patch("zspace.auth.VUEX_PATH") as mock_path, \
                patch("zspace.auth.open") as mock_open:
            mock_zspace.exists.return_value = True
            mock_path.exists.return_value = True
            mock_file = __import__("io").StringIO(mock_data)
            mock_open.return_value.__enter__.return_value = mock_file
            result = _load_vuex()
            assert result == {"app": {"localPort": 12345}}

    def test_cache_hit_returns_same_value(self):
        import zspace.auth
        zspace.auth._vuex_cache = None
        mock_data = '{"state": {"app": {"localPort": 12345}}}'
        with patch("zspace.auth.ZSPACE_DIR") as mock_zspace, \
                patch("zspace.auth.VUEX_PATH") as mock_path, \
                patch("zspace.auth.open") as mock_open:
            mock_zspace.exists.return_value = True
            mock_path.exists.return_value = True
            mock_file = __import__("io").StringIO(mock_data)
            mock_open.return_value.__enter__.return_value = mock_file
            first = _load_vuex()
            second = _load_vuex()
            assert first is second

    def test_missing_zspace_dir(self):
        import zspace.auth
        zspace.auth._vuex_cache = None
        with patch("zspace.auth.ZSPACE_DIR") as mock_zspace:
            mock_zspace.exists.return_value = False
            with pytest.raises(AuthError, match="未找到 zspace 客户端"):
                _load_vuex()

    def test_missing_vuex_file(self):
        import zspace.auth
        zspace.auth._vuex_cache = None
        with patch("zspace.auth.ZSPACE_DIR") as mock_zspace, \
                patch("zspace.auth.VUEX_PATH") as mock_path:
            mock_zspace.exists.return_value = True
            mock_path.exists.return_value = False
            with pytest.raises(AuthError, match="未登录"):
                _load_vuex()


class TestAuthError:
    def test_auth_error_message(self):
        err = AuthError("测试错误")
        assert str(err) == "测试错误"

    def test_auth_error_type(self):
        assert issubclass(AuthError, RuntimeError)


class TestBuildCookies:
    def test_build_cookies_basic(self):
        vuex = {
            "nas": {"nasId": "NAS001", "locale": "zh-CN"},
            "user": {"token": "abc123", "username": "test_user"},
            "app": {"deviceId": "dev-001"},
        }
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = vuex
            cookies = build_cookies()

        assert cookies["token"] == "abc123"
        assert cookies["username"] == "test_user"
        assert cookies["nas_id"] == "NAS001"
        assert cookies["_l"] == "zh-CN"
        assert cookies["device_id"] == "dev-001"
        assert cookies["version"] == "2.3.2026060701"
        assert cookies["plat"] == "web"

    def test_build_cookies_missing_keys(self):
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = {}
            cookies = build_cookies()

        assert cookies["token"] == ""
        assert cookies["username"] == ""
        assert cookies["nas_id"] == ""
        assert cookies["_l"] == ""

    def test_build_cookies_full_data(self):
        vuex = {
            "nas": {
                "cloudPubKey": "cpk",
                "cloudPubKeyId": "cpkid",
                "sign": "sig",
                "nasPubKey": "npk",
                "nasId": "nid",
                "color": "blue",
                "devicePdt": "pdt",
                "deviceMode": "mode",
                "locale": "en",
            },
            "user": {
                "token": "tok",
                "username": "admin",
                "qcname": "QC",
                "isMaster": 1,
            },
            "app": {
                "deviceId": "did",
                "device": "MacBook Pro",
            },
        }
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = vuex
            cookies = build_cookies()

        assert cookies["cloudPubKey"] == "cpk"
        assert cookies["cloudPubKeyId"] == "cpkid"
        assert cookies["sign"] == "sig"
        assert cookies["nasPubKey"] == "npk"
        assert cookies["deviceColor"] == "blue"
        assert cookies["devicePdt"] == "pdt"
        assert cookies["deviceMode"] == "mode"
        assert cookies["isMaster"] == "1"
        assert cookies["qcname"] == "QC"
        assert cookies["device"] == "MacBook Pro"


class TestBuildCookieHeader:
    def test_cookie_header_format(self):
        vuex = {
            "user": {"token": "abc", "username": "test"},
            "nas": {"locale": "zh-CN"},
            "app": {"deviceId": "dev1"},
        }
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = vuex
            header = build_cookie_header()

        assert "zenithtoken=abc" in header
        assert "token=abc" in header
        assert "username=test" in header
        assert "; " in header

    def test_cookie_header_value_encoding(self):
        vuex = {
            "user": {"token": "abc", "username": "中文用户"},
            "nas": {"locale": "zh-CN"},
            "app": {"device": "我的设备\n"},
        }
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = vuex
            header = build_cookie_header()

        assert "%E4%B8%AD%E6%96%87%E7%94%A8%E6%88%B7" in header
        assert "username" in header


class TestBuildHeaders:
    def test_headers_structure(self):
        vuex = {
            "user": {"token": "abc", "username": "test"},
            "nas": {"locale": "en"},
            "app": {"deviceId": "dev1"},
        }
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = vuex
            with patch("zspace.auth.get_base_url") as mock_url:
                mock_url.return_value = "http://127.0.0.1:13579"
                headers = build_headers(path="/sata12/my/data")

        assert "Cookie" in headers
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/x-www-form-urlencoded"
        assert "Referer" in headers
        assert "127.0.0.1" in headers["Referer"]
        assert "User-Agent" in headers
        assert "Mozilla/5.0" in headers["User-Agent"]

    def test_headers_referer_path_encoding(self):
        vuex = {
            "user": {"token": "abc", "username": "test"},
            "nas": {"locale": "en"},
            "app": {"deviceId": "dev1"},
        }
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = vuex
            with patch("zspace.auth.get_base_url") as mock_url:
                mock_url.return_value = "http://127.0.0.1:13579"
                headers = build_headers(path="中文路径")

        assert "%E4%B8%AD%E6%96%87%E8%B7%AF%E5%BE%84" in headers["Referer"]
