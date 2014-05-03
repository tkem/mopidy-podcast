from __future__ import unicode_literals

import collections
import itertools
import logging
import operator
import urllib2

from . import Extension
from .cachetools import cachedmethod
from .directory import PodcastDirectory
from .models import Podcast, Episode, Ref

logger = logging.getLogger(__name__)


def _cache(cache_size=0, cache_ttl=0, **kwargs):
    from .cachetools import LRUCache
    import time

    expires = {}

    # TODO: integrate with cachetools
    class Cache(LRUCache):

        def __getitem__(self, key):
            if expires[key] < time.time():
                del self[key]
            return super(Cache, self).__getitem__(key)

        def __setitem__(self, key, value):
            if len(self) >= self.maxsize:
                now = time.time()
                for key in self.keys():
                    if expires[key] < now:
                        del self[key]
            super(Cache, self).__setitem__(key, value)
            expires[key] = time.time() + cache_ttl

        def __delitem__(self, key):
            super(Cache, self).__delitem__(key)
            del expires[key]

    return Cache(cache_size)


def _browse_episodes(podcast, limit=None):
    refs = []
    for e in podcast.episodes:
        if not e.uri:
            continue
        if limit and len(refs) >= limit:
            break
        refs.append(Ref.episode(uri=e.uri, name=e.title))
    return refs


def _search_episodes(podcast, terms, attr=None, limit=None):
    terms = [term.lower() for term in terms if term]
    if attr is None:
        getter = operator.attrgetter('title', 'author', 'description')
    elif hasattr(Episode, attr):
        getter = operator.attrgetter(attr)
    else:
        logger.warn('Invalid podcast episode attribute: %r', attr)
        return None

    refs = []
    for e in podcast.episodes:
        if not e.uri:
            continue
        if limit and len(refs) >= limit:
            break
        if all(term in unicode(getter(e) or '').lower() for term in terms):
            refs.append(Ref.episode(uri=e.uri, name=e.title))
    return refs


def _by_pubdate(e):
    return e.pubdate or ''


class FeedsDirectory(PodcastDirectory):

    Entry = collections.namedtuple('Entry', 'ref index pubdate')

    name = 'feeds'

    uri_schemes = ['http', 'https', 'file']

    def __init__(self, config):
        super(FeedsDirectory, self).__init__(config)
        self.display_name = config[Extension.ext_name]['feeds_label']
        self._timeout = config[Extension.ext_name]['timeout']
        self._feeds = config[Extension.ext_name]['feeds']
        self._cache = _cache(**config[Extension.ext_name])
        self._podcasts = []
        self._episodes = []

    @cachedmethod(getcache=operator.attrgetter('_cache'))
    def get(self, uri):
        from contextlib import closing
        with closing(urllib2.urlopen(uri, timeout=self._timeout)) as source:
            return Podcast.parse(source, uri)

    def browse(self, uri, limit=None):
        if not uri or uri == '/':
            return [e.ref for e in self._podcasts]
        else:
            return _browse_episodes(self.get(uri), limit)

    def search(self, uri, terms, attr=None, type=None, limit=None):
        if not uri or uri == '/':
            return self._search_index(terms, attr, type, limit)
        elif type is None or type == Ref.EPISODE:
            return _search_episodes(self.get(uri), terms, attr, limit)
        else:
            return None

    def refresh(self, uri=None):
        podcasts = []
        episodes = []
        for feedurl in self._feeds:
            try:
                podcast = self.get(feedurl)
            except Exception as e:
                logger.error('Error loading podcast %s: %r', feedurl, e)
                continue  # TODO: keep existing entry?
            e = self._index_podcast(podcast, feedurl)
            for episode in podcast.episodes:
                episodes.append(self._index_episode(episode, feedurl, e.index))
            podcasts.append(e)
        podcasts.sort(key=_by_pubdate, reverse=True)
        episodes.sort(key=_by_pubdate, reverse=True)
        self._podcasts = podcasts
        self._episodes = episodes

    def _search_index(self, terms, attr=None, type=None, limit=None):
        terms = [term.lower() for term in terms if term]
        if type is None:
            entries = itertools.chain(self._podcasts, self._episodes)
        elif type == Ref.PODCAST:
            entries = iter(self._podcasts)
        elif type == Ref.EPISODE:
            entries = iter(self._episodes)
        else:
            logger.warn('Unknown podcast search type: %r', type)
            return None

        refs = []
        for e in entries:
            if limit and len(refs) >= limit:
                break
            if all(term in e.index.get(attr, '') for term in terms):
                refs.append(e.ref)
        return refs

    def _index_podcast(self, podcast, feedurl):
        ref = Ref.podcast(uri=feedurl, name=podcast.title)
        index = {
            'title': (podcast.title or '').lower(),
            'author': (podcast.author or '').lower(),
            'category': (podcast.category or '').lower(),
            'description': (podcast.description or '').lower(),
            'keywords': ','.join(podcast.keywords).lower()
        }
        index[None] = '\n'.join(index.values())
        return self.Entry(ref, index, podcast.pubdate)

    def _index_episode(self, episode, feedurl, defaults):
        ref = Ref.episode(uri=episode.uri, name=episode.title)
        index = defaults.copy()
        for name in ('title', 'author', 'description'):
            if getattr(episode, name):
                index[name] = getattr(episode, name).lower()
        if episode.keywords:
            index['keywords'] = ','.join(episode.keywords).lower()
        index[None] = '\n'.join(index.values())
        return self.Entry(ref, index, episode.pubdate)
