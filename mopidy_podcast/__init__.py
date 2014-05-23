from __future__ import unicode_literals

from mopidy import config, ext

__version__ = '1.0.0'


class Extension(ext.Extension):

    dist_name = 'Mopidy-Podcast'
    ext_name = 'podcast'
    version = __version__

    def get_default_config(self):
        import os
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['root_name'] = config.String()
        schema['browse_limit'] = config.Integer(optional=True, minimum=1)
        schema['search_limit'] = config.Integer(optional=True, minimum=1)
        schema['search_details'] = config.Boolean()
        schema['update_interval'] = config.Integer(minimum=60)
        # feeds directory provider config
        schema['feeds'] = config.List(optional=True)
        schema['feeds_root_name'] = config.String()
        schema['feeds_cache_size'] = config.Integer(minimum=1)
        schema['feeds_cache_ttl'] = config.Integer(minimum=1)
        schema['feeds_timeout'] = config.Integer(optional=True, minimum=1)
        # no longer used/needed
        schema['browse_label'] = config.Deprecated()
        schema['cache_size'] = config.Deprecated()
        schema['cache_ttl'] = config.Deprecated()
        schema['feeds_label'] = config.Deprecated()
        schema['search_results'] = config.Deprecated()
        schema['sort_order'] = config.Deprecated()
        schema['timeout'] = config.Deprecated()
        return schema

    def setup(self, registry):
        from .backend import PodcastBackend
        from .feeds import FeedsDirectory

        registry.add('backend', PodcastBackend)
        registry.add('podcast:directory', FeedsDirectory)

        PodcastBackend.directories = registry['podcast:directory']
