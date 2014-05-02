from __future__ import unicode_literals

from .models import Podcast, Episode, Ref


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
            return Podcast.parse(source, uri)

    def browse(self, uri, limit=None):
        """Browse directories, podcasts and episodes at the given `uri`."""
        refs = []
        for e in self.get(uri).episodes:
            if not e.uri:
                continue
            if limit and len(refs) >= limit:
                break
            refs.append(Ref.episode(uri=e.uri, name=e.title))
        return refs

    def search(self, terms, attr=None, type=None, uri=None, limit=None):
        """Search for podcasts and/or episodes where `attribute`
        contains `terms`.

        """
        import operator
        terms = [term.lower() for term in terms]
        if attr is None:
            getter = operator.attrgetter('title', 'author', 'description')
        elif hasattr(Episode, attr):
            getter = operator.attrgetter(attr)
        else:
            return None
        if type is not None and type != Ref.EPISODE:
            return None
        refs = []
        for e in self.get(uri).episodes:
            if not e.uri:
                continue
            if limit and len(refs) >= limit:
                break
            if all(term in unicode(getter(e) or '').lower() for term in terms):
                refs.append(Ref.episode(uri=e.uri, name=e.title))
        return refs

    def update(self):
        """Update the podcast directory."""
        pass
