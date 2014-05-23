from __future__ import unicode_literals


class PodcastDirectory(object):
    """Podcast directory provider."""

    name = None
    """Name of the podcast directory implementation."""

    root_name = None
    """Name of the root directory for browsing."""

    uri_schemes = []
    """List of URI schemes the directory can handle."""

    def __init__(self, config):
        pass

    def get(self, uri):
        """Return a podcast for the given `uri`."""
        raise NotImplementedError

    def browse(self, uri, limit=None):
        """Browse directories, podcasts and episodes at the given `uri`."""
        raise NotImplementedError

    def search(self, uri, terms, attr=None, type=None, limit=None):
        """Search podcasts and episodes at the given `uri` for `terms`."""
        raise NotImplementedError

    def refresh(self, uri=None):
        """Refresh the podcast directory."""
        pass
