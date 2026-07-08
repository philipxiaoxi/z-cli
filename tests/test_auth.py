"""认证模块测试。"""

from unittest.mock import patch

from zspace.auth import get_base_url


class TestGetBaseUrl:
    def test_default_port(self):
        with patch("zspace.auth._load_vuex") as mock_load:
            mock_load.return_value = {"app": {"localPort": 13579}}
            assert get_base_url() == "http://127.0.0.1:13579"

    def test_environment_variable(self, monkeypatch):
        monkeypatch.setenv("ZSPACE_HOST", "http://192.168.1.100:8888")
        assert get_base_url() == "http://192.168.1.100:8888"
