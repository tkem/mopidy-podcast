from __future__ import unicode_literals

import cachetools
import collections
import contextlib
import datetime
import itertools
import logging
import operator
import uritools
import urllib2

from . import Extension
from .directory import PodcastDirectory
from .models import Episode, Ref
from .rssfeed import parse_rss

_PODCAST_SEARCH_ATTRS = ('title', 'author', 'category', 'subtitle', 'summary')

_EPISODE_SEARCH_ATTRS = ('title', 'author', 'subtitle', 'summary')

logger = logging.getLogger(__name__)


def _feeds_cache(feeds_cache_size=None, feeds_cache_ttl=None, **kwargs):
    """Cache factory"""
    if feeds_cache_size is None:
        return None  # mainly for testing/debugging
    elif feeds_cache_ttl is None:
        return cachetools.LRUCache(feeds_cache_size)
    else:
        return cachetools.TTLCache(feeds_cache_size, feeds_cache_ttl)


def _pubdate(model):
    return model.pubdate or datetime.datetime.min


class FeedsDirectory(PodcastDirectory):

    IndexEntry = collections.namedtuple('Entry', 'ref index pubdate')

    name = 'feeds'

    uri_schemes = ['file', 'ftp', 'http', 'https']

    def __init__(self, config):
        super(FeedsDirectory, self).__init__(config)
        self._config = ext_config = config[Extension.ext_name]
        self._cache = _feeds_cache(**ext_config)
        self._podcasts = []
        self._episodes = []

        self.root_name = ext_config['feeds_root_name']  # for browsing

    @cachetools.cachedmethod(operator.attrgetter('_cache'))
    def get(self, uri):
        uri, _ = uritools.uridefrag(uri)  # remove fragment, if any
        timeout = self._config['feeds_timeout']
        with contextlib.closing(urllib2.urlopen(uri, timeout=timeout)) as src:
            return parse_rss(src)  # FIXME: check Content-Type header?

    def browse(self, uri, limit=None):
        if not uri or uri == '/':
            return [e.ref for e in self._podcasts]
        else:
            return self._browse_episodes(uri, limit)

    def search(self, uri, terms, attr=None, type=None, limit=None):
        if not uri or uri == '/':
            return self._search_index(terms, attr, type, limit)
        elif type is None or type == Ref.EPISODE:
            return self._search_episodes(uri, terms, attr, limit)
        else:
            return None

    def refresh(self, uri=None):
        podcasts = {p.ref.uri: p for p in self._podcasts}
        episodes = {e.ref.uri: e for e in self._episodes}
        self._cache.clear()
        for feedurl in self._config['feeds']:
            try:
                podcast = self.get(feedurl)
            except Exception as e:
                logger.error('Error loading podcast %s: %s', feedurl, e)
                continue  # keep existing entry
            try:
                p = self._index_podcast(podcast)
                for episode in podcast.episodes:
                    e = self._index_episode(episode, p.index)
                    episodes[e.ref.uri] = e
                podcasts[p.ref.uri] = p
            except Exception as e:
                logger.error('Error indexing podcast %s: %s', feedurl, e)
        self._podcasts = sorted(podcasts.values(), key=_pubdate, reverse=True)
        self._episodes = sorted(episodes.values(), key=_pubdate, reverse=True)

    def _browse_episodes(self, uri, limit=None):
        refs = []
        for e in self.get(uri).episodes:
            if limit and len(refs) >= limit:
                break
            if not e.uri:  # TODO: filter by media type?
                continue
            refs.append(Ref.episode(uri=e.uri, name=e.title))
        return refs

    def _search_episodes(self, uri, terms, attr=None, limit=None):
        if attr is None:
            getter = operator.attrgetter(*_EPISODE_SEARCH_ATTRS)
        elif hasattr(Episode, attr):
            getter = operator.attrgetter(attr)
        else:
            return None
        terms = map(unicode.lower, terms)

        refs = []
        for e in self.get(uri).episodes:
            if limit and len(refs) >= limit:
                break
            if not e.uri:  # TODO: filter by media type?
                continue
            if all(term in unicode(getter(e) or '').lower() for term in terms):
                refs.append(Ref.episode(uri=e.uri, name=e.title))
        return refs

    def _search_index(self, terms, attr=None, type=None, limit=None):
        if type is None:
            entries = itertools.chain(self._podcasts, self._episodes)
        elif type == Ref.PODCAST:
            entries = iter(self._podcasts)
        elif type == Ref.EPISODE:
            entries = iter(self._episodes)
        else:
            return None
        terms = map(unicode.lower, terms)

        refs = []
        for e in entries:
            if limit and len(refs) >= limit:
                break
            if all(term in e.index.get(attr, '') for term in terms):
                refs.append(e.ref)
        return refs

    def _index_podcast(self, podcast):
        ref = Ref.podcast(uri=podcast.uri, name=podcast.title)
        index = {}
        for name in _PODCAST_SEARCH_ATTRS:
            if getattr(podcast, name):
                index[name] = getattr(podcast, name).lower()
        index[None] = '\n'.join(index.values())
        return self.IndexEntry(ref, index, podcast.pubdate)

    def _index_episode(self, episode, defaults):
        ref = Ref.episode(uri=episode.uri, name=episode.title)
        index = defaults.copy()
        for name in _EPISODE_SEARCH_ATTRS:
            if getattr(episode, name):
                index[name] = getattr(episode, name).lower()
        index[None] = '\n'.join(index.values())
        return self.IndexEntry(ref, index, episode.pubdate)
