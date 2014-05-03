from __future__ import unicode_literals


class PodcastDirectory(object):
    """Podcast directory interface.

    Mopidy-Podcast extensions that wish to provide alternate podcast
    directory services need to subclass :class:`PodcastDirectory` and
    install and configure it with a Mopidy extension.  Directory
    subclasses need to be added to :class:`Mopidy.ext.Registry` with
    the key `podcast:directory`.

    """

    name = None
    """Name of the podcast directory implementation."""

    display_name = None
    """User-friendly name for browsing the directory."""

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
        """Search for podcasts and/or episodes."""
        raise NotImplementedError

    def refresh(self, uri=None):
        """Update the podcast directory or a given `uri`."""
        pass
