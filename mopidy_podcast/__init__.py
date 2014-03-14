from __future__ import unicode_literals

from mopidy import config, ext

__version__ = '0.3.0'


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
        schema['directories'] = config.List()
        schema['browse_label'] = config.String()
        schema['search_limit'] = config.Integer(optional=True, minimum=1)
        schema['max_episodes'] = config.Integer(optional=True, minimum=1)
        schema['sort_order'] = config.String(choices=['asc', 'desc'])
        schema['update_interval'] = config.Integer(minimum=1)
        schema['cache_size'] = config.Integer(optional=True, minimum=1)
        schema['cache_ttl'] = config.Integer(optional=True, minimum=1)
        schema['timeout'] = config.Integer(optional=True, minimum=1)

        # feeds directory provider config
        schema['feeds'] = config.List(optional=True)
        schema['feeds_label'] = config.String(optional=True)

        # no longer used
        schema['feed_urls'] = config.Deprecated()
        return schema

    def setup(self, registry):
        from .backend import PodcastBackend
        from .feeds import FeedsDirectory
        registry.add('backend', PodcastBackend)
        registry.add('podcast:directory', FeedsDirectory)
        PodcastBackend.registry = registry


class PodcastDirectory(object):
    """Podcast directory interface.

    Extensions that wish to provide a alternate podcast directories
    need to subclass this class and install and configure it with an
    extension.
    """

    # search attributes
    AUTHOR = 'author'
    CATEGORY = 'category'
    DESCRIPTION = 'description'
    KEYWORDS = 'keywords'
    TITLE = 'title'

    name = None
    """Name of the podcast directory implementation.

    This must be overridden by subclasses.
    """

    display_name = None
    """Display name to use for browsing.

    This must be overridden by subclasses which support browsing.
    """

    def __init__(self, backend):
        self.backend = backend

    def get(self, uri, cached=True):
        """Return a podcast for the given `uri`.
        """

        from .models import Podcast
        from urllib2 import urlopen

        if cached and self.backend.cache:
            try:
                return self.backend.cache[uri]
            except KeyError:
                pass
        # urlopen does not return a context manager...
        source = urlopen(uri, timeout=self.backend.timeout)
        try:
            podcast = Podcast.parse(source)
        finally:
            source.close()
        if self.backend.cache is not None:
            self.backend.cache[uri] = podcast
        return podcast

    def browse(self, uri):
        """Browse directory for given `uri`.
        """
        raise NotImplementedError

    def search(self, terms=None, attribute=None, limit=None):
        """Search directory.
        """
        raise NotImplementedError

    def refresh(self, uri=None):
        """Refresh directory.
        """
        pass
