import pathlib

import pkg_resources

from mopidy import config, ext, httpclient

__version__ = pkg_resources.get_distribution("Mopidy-Podcast").version


class Extension(ext.Extension):

    dist_name = "Mopidy-Podcast"
    ext_name = "podcast"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["browse_root"] = config.String(optional=True)
        schema["browse_order"] = config.String(choices=["asc", "desc"])
        schema["lookup_order"] = config.String(choices=["asc", "desc"])
        schema["cache_size"] = config.Integer(minimum=1)
        schema["cache_ttl"] = config.Integer(minimum=1)
        schema["timeout"] = config.Integer(optional=True, minimum=1)
        # no longer used
        schema["browse_limit"] = config.Deprecated()
        schema["search_limit"] = config.Deprecated()
        schema["search_details"] = config.Deprecated()
        schema["update_interval"] = config.Deprecated()
        schema["feeds"] = config.Deprecated()
        schema["feeds_root_name"] = config.Deprecated()
        schema["feeds_cache_size"] = config.Deprecated()
        schema["feeds_cache_ttl"] = config.Deprecated()
        schema["feeds_timeout"] = config.Deprecated()
        return schema

    def setup(self, registry):
        from .backend import PodcastBackend

        registry.add("backend", PodcastBackend)

    @classmethod
    def get_url_opener(cls, config):
        from urllib.request import ProxyHandler, build_opener

        proxy = httpclient.format_proxy(config["proxy"])
        if proxy:
            handlers = [ProxyHandler({"http": proxy, "https": proxy})]
        else:
            handlers = []
        opener = build_opener(*handlers)
        user_agent = f"{cls.dist_name}/{cls.version}"
        opener.addheaders = [
            ("User-agent", httpclient.format_user_agent(user_agent))
        ]
        return opener
