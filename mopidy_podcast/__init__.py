from __future__ import unicode_literals

from mopidy import config, ext

__version__ = '0.4.0'


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
        schema['browse_label'] = config.String()
        schema['browse_limit'] = config.Integer(optional=True, minimum=1)
        schema['search_limit'] = config.Integer(optional=True, minimum=1)
        schema['search_results'] = config.String(choices=['title', 'full'])
        schema['sort_order'] = config.String(choices=['asc', 'desc'])
        schema['update_interval'] = config.Integer(minimum=1)
        schema['cache_size'] = config.Integer(minimum=1)
        schema['cache_ttl'] = config.Integer(minimum=1)
        schema['timeout'] = config.Integer(optional=True, minimum=1)

        # feeds directory provider config
        schema['feeds'] = config.List(optional=True)
        schema['feeds_label'] = config.String(optional=True)

        return schema

    def setup(self, registry):
        from .backend import PodcastBackend
        from .feeds import FeedsDirectory

        registry.add('backend', PodcastBackend)
        registry.add('podcast:directory', FeedsDirectory)

        PodcastBackend.directories = registry['podcast:directory']
