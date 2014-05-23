from __future__ import unicode_literals

import collections
import contextlib
import datetime
import email.utils
import itertools
import logging
import operator
import re
import time
import urllib2
import xml.etree.ElementTree

from . import Extension
from .cachetools import LRUCache, cachedmethod
from .directory import PodcastDirectory
from .models import Podcast, Episode, Image, Enclosure, Ref
from .uritools import uridefrag

_DURATION_RE = re.compile(r"""
(?:
    (?:(?P<hours>\d+):)?
    (?P<minutes>\d+):
)?
(?P<seconds>\d+)
""", flags=re.VERBOSE)

_NAMESPACES = {
    'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'
}

_PODCAST_SEARCH_ATTRS = ('title', 'author', 'category', 'subtitle', 'summary')

_EPISODE_SEARCH_ATTRS = ('title', 'author', 'subtitle', 'summary')

logger = logging.getLogger(__name__)


def _getchannel(uri, timeout=None):
    with contextlib.closing(urllib2.urlopen(uri, timeout=timeout)) as source:
        channel = xml.etree.ElementTree.parse(source).find('channel')
    if channel is None:
        raise TypeError('Error parsing %s' % uri)
    return channel


def _gettag(etree, tag, convert=None, namespaces=_NAMESPACES):
    e = etree.find(tag, namespaces=namespaces)
    if e is None:
        return None
    elif convert:
        return convert(e)
    elif e.text:
        return e.text.strip()
    else:
        return None


def _to_bool(e):
    return e.text.strip().lower() == 'yes' if e.text else None


def _to_int(e):
    return int(e.text) if e.text and e.text.isdigit() else None


def _to_datetime(e):
    try:
        timestamp = email.utils.mktime_tz(email.utils.parsedate_tz(e.text))
    except AttributeError:
        return None
    except TypeError:
        return None
    return datetime.datetime.utcfromtimestamp(timestamp)


def _to_timedelta(e):
    try:
        groups = _DURATION_RE.match(e.text).groupdict('0')
    except AttributeError:
        return None
    except TypeError:
        return None
    return datetime.timedelta(**{k: int(v) for k, v in groups.items()})


def _to_category(e):
    return e.get('text')


def _to_image(e):
    kwargs = {}
    # handle both RSS and itunes images
    kwargs['uri'] = e.get('href', _gettag(e, 'url'))
    kwargs['title'] = _gettag(e, 'title')
    for name in ('width', 'height'):
        kwargs[name] = _gettag(e, name, _to_int)
    return Image(**kwargs)


def _to_enclosure(e):
    uri = e.get('url')
    type = e.get('type')
    length = int(e.get('length')) if e.get('length', '').isdigit() else None
    return Enclosure(uri=uri, type=type, length=length)


def _to_episode(e, feedurl):
    kwargs = {
        'title': _gettag(e, 'title'),
        'guid': _gettag(e, 'guid'),
        'pubdate': _gettag(e, 'pubDate', _to_datetime),
        'author': _gettag(e, 'itunes:author'),
        'block': _gettag(e, 'itunes:block', _to_bool),
        'image': _gettag(e, 'itunes:image', _to_image),
        'duration': _gettag(e, 'itunes:duration', _to_timedelta),
        'explicit': _gettag(e, 'itunes:explicit', _to_bool),  # TODO: "clean"
        'order': _gettag(e, 'itunes:order', _to_int),
        'subtitle': _gettag(e, 'itunes:subtitle'),
        'summary': _gettag(e, 'itunes:summary'),
        'enclosure': _gettag(e, 'enclosure', _to_enclosure)

    }
    if not kwargs['summary']:
        kwargs['summary'] = _gettag(e, 'description')
    if not kwargs['guid'] and kwargs['enclosure']:
        kwargs['guid'] = kwargs['enclosure'].uri
    if kwargs['enclosure'] and kwargs['enclosure'].uri:
        kwargs['uri'] = feedurl + '#' + kwargs['enclosure'].uri
    return Episode(**kwargs)


def _pubdate(model):
    return model.pubdate or datetime.datetime.min


class FeedsCache(LRUCache):

    def __init__(self, maxsize, ttl, timer=time.time):
        super(FeedsCache, self).__init__(maxsize)
        self.__expires = {}
        self.__timer = timer
        self.__ttl = ttl

    def __getitem__(self, key):
        if self.__expires[key] < self.__timer():
            logger.debug('Cached feed expired: %s', key)
            del self[key]
        return super(FeedsCache, self).__getitem__(key)

    def __setitem__(self, key, value):
        t = self.__timer()
        for k in self.keys():
            if self.__expires[k] < t:
                logger.debug('Cached feed expired: %s', k)
                del self[k]
        super(FeedsCache, self).__setitem__(key, value)
        self.__expires[key] = self.__timer() + self.__ttl

    def __delitem__(self, key):
        super(FeedsCache, self).__delitem__(key)
        del self.__expires[key]


class FeedsDirectory(PodcastDirectory):

    IndexEntry = collections.namedtuple('Entry', 'ref index pubdate')

    name = 'feeds'

    uri_schemes = ['file', 'ftp', 'http', 'https']

    def __init__(self, config):
        super(FeedsDirectory, self).__init__(config)
        self._config = config[Extension.ext_name]
        self._cache = FeedsCache(
            self._config['feeds_cache_size'],
            self._config['feeds_cache_ttl']
        )
        self._podcasts = []
        self._episodes = []

        self.root_name = self._config['feeds_root_name']  # for browsing

    @cachedmethod(getcache=operator.attrgetter('_cache'))
    def get(self, uri):
        channel = _getchannel(uri, self._config['feeds_timeout'])

        kwargs = {}
        kwargs['uri'], _ = uridefrag(uri)  # strip fragment if present
        for name in ('title', 'link', 'copyright', 'language'):
            kwargs[name] = _gettag(channel, name)
        for name in ('author', 'subtitle', 'summary'):
            kwargs[name] = _gettag(channel, 'itunes:' + name)
        for name in ('block', 'complete', 'explicit'):  # TODO: clean
            kwargs[name] = _gettag(channel, 'itunes:' + name, _to_bool)
        kwargs['pubdate'] = _gettag(channel, 'pubDate', _to_datetime)
        kwargs['category'] = _gettag(channel, 'itunes:category', _to_category)
        kwargs['newfeedurl'] = _gettag(channel, 'itunes:new-feed-url')
        kwargs['image'] = _gettag(channel, 'image', _to_image)

        if not kwargs['summary']:
            kwargs['summary'] = _gettag(channel, 'description')
        if not kwargs['image']:  # TBD: prefer iTunes image over RSS image?
            kwargs['image'] = _gettag(channel, 'itunes:image', _to_image)

        episodes = []
        for item in channel.iter(tag='item'):
            try:
                episodes.append(_to_episode(item, kwargs['uri']))
            except Exception as e:
                logger.warn('Skipping episode for %s: %s', uri, e)
        kwargs['episodes'] = sorted(episodes, key=_pubdate, reverse=True)

        return Podcast(**kwargs)

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
