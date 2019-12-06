from unittest import mock
from urllib.request import FileHandler, HTTPHandler, HTTPSHandler

import pytest
from mopidy_podcast import Extension, backend


def test_get_default_config():
    config = Extension().get_default_config()
    assert "[" + Extension.ext_name + "]" in config
    assert "enabled = true" in config


def test_get_config_schema():
    schema = Extension().get_config_schema()
    assert "browse_root" in schema
    assert "browse_order" in schema
    assert "lookup_order" in schema
    assert "cache_size" in schema
    assert "cache_ttl" in schema
    assert "timeout" in schema


def test_setup():
    registry = mock.Mock()
    Extension().setup(registry)
    registry.add.assert_called_once_with("backend", backend.PodcastBackend)


@pytest.mark.parametrize(
    "url,handler,method,proxy_config",
    [
        ("file://example.com/feed.xml", FileHandler, "file_open", {}),
        ("http://example.com/feed.xml", HTTPHandler, "http_open", {}),
        ("https://example.com/feed.xml", HTTPSHandler, "https_open", {},),
        (
            "http://example.com/feed.xml",
            HTTPHandler,
            "http_open",
            {"scheme": "http", "hostname": "localhost", "port": 9999},
        ),
        (
            "http://example.com/feed.xml",
            HTTPSHandler,
            "https_open",
            {"scheme": "https", "hostname": "localhost", "port": 9999},
        ),
    ],
)
def test_get_url_opener(url, handler, method, proxy_config):
    opener = Extension.get_url_opener({"proxy": proxy_config})
    with mock.patch.object(handler, method) as mock_open:
        try:
            opener.open(url)
        except Exception:
            pass
    assert mock_open.mock_calls
    (req,), _ = mock_open.call_args
    if req.header_items():
        user_agent = f"{Extension.dist_name}/{Extension.version}"
        assert user_agent in req.get_header("User-agent")
    if proxy_config:
        assert req.type == proxy_config["scheme"]
        assert req.host == "{hostname}:{port}".format(**proxy_config)
        assert req.selector == url
    assert url == req.get_full_url()
