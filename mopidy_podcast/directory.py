from __future__ import unicode_literals

from .models import Podcast, Ref

class PodcastDirectory(object):
    """Podcast directory interface.

    Mopidy-Podcast extensions that wish to provide alternate podcast
    directory services need to subclass :class:`PodcastDirectory` and
    install and configure it with a Mopidy extension.

    """

    TITLE = 'title'
    """Search attribute for matching a podcast's or episode's title."""

    AUTHOR = 'author'
    """Search attribute for matching a podcast or episode author's
    name.

    """

    CATEGORY = 'category'
    """Search attribute for matching a podcast category."""

    DESCRIPTION = 'description'
    """Search attribute for matching a podcast's or episode's
    description.

    """

    KEYWORDS = 'keywords'
    """Search attribute for matching a podcast's or episode's keywords.

    """

    name = None
    """Name of the podcast directory implementation."""

    display_name = None
    """User-friendly name for browsing."""

    __timeout = None

    def __init__(self, config, timeout):
        self.__timeout = timeout

    def get(self, uri):
        """Return a podcast for the given `uri`."""
        from contextlib import closing
        from urllib2 import urlopen

        with closing(urlopen(uri, timeout=self.__timeout)) as source:
            return Podcast.parse(source)

    def browse(self, uri, limit=None):
        """Browse directories, podcasts and episodes at the given `uri`."""
        refs = []
        for e in self.get(uri).episodes:
            if limit and len(refs) >= limit:
                break
            if not e.enclosure or not e.enclosure.url:
                continue
            ref = Ref.episode(uri=uri+'#'+e.enclosure.url, name=e.title)
            refs.append(ref)
        return refs

    def search(self, terms=None, attribute=None, type=None, limit=None):
        """Search for podcasts and/or episodes where `attribute`
        contains `terms`.

        """
        return None

    def update(self):
        """Update the podcast directory."""
        pass
