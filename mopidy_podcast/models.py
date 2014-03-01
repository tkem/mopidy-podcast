from __future__ import unicode_literals

from collections import namedtuple
from datetime import datetime, timedelta

import logging
import re

import mopidy.models

DURATION_RE = re.compile(r"""
(?:
    (?:(?P<hours>\d+):)?
    (?P<minutes>\d+):
)?
(?P<seconds>\d+)
""", flags=re.VERBOSE)

NAMESPACES = {
    'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'
}

logger = logging.getLogger(__name__)


def _gettag(etree, tag, convert=None, namespaces=NAMESPACES):
    e = etree.find(tag, namespaces=namespaces)
    if e is None:
        return None
    elif convert:
        return convert(e)
    elif e.text:
        return e.text.strip()
    else:
        return None


def _gettags(etree, tag, convert=None):
    tags = []
    for e in etree.iter(tag=tag):
        if convert:
            result = convert(e)
        elif e.text:
            result = e.text.strip()
        else:
            result = None
        if result is not None:
            tags.append(result)
    return tags


def _to_datetime(e):
    from email.utils import mktime_tz, parsedate_tz
    try:
        timestamp = mktime_tz(parsedate_tz(e.text))
    except AttributeError:
        logger.warn('Invalid podcast date element: %s', e.text)
        return None
    except TypeError:
        logger.warn('Invalid podcast date element: %s', e.text)
        return None
    return datetime.fromtimestamp(timestamp)


def _to_timedelta(e):
    try:
        groups = DURATION_RE.match(e.text).groupdict('0')
    except AttributeError:
        logger.warn('Invalid podcast duration element: %s', e.text)
        return None
    except TypeError:
        logger.warn('Invalid podcast duration element: %s', e.text)
        return None
    return timedelta(**{k: int(v) for k, v in groups.items()})


def _to_wordlist(e):
    return [s.strip() for s in e.text.split(',')] if e.text else None


def _to_image(e):
    return Podcast.Image(
        e.get('url'), e.get('title'), e.get('link'),
        e.get('width'), e.get('height'), e.get('description')
    )


def _to_enclosure(e):
    return Episode.Enclosure(e.get('url'), e.get('length'), e.get('type'))


def _to_episode(e):
    kwargs = {}
    for name in ('title', 'link', 'description', 'guid'):
        kwargs[name] = _gettag(e, name)
    kwargs['pubdate'] = _gettag(e, 'pubDate', _to_datetime)
    kwargs['enclosure'] = _gettag(e, 'enclosure', _to_enclosure)
    for name in ('author', 'block', 'explicit', 'subtitle', 'summary'):
        kwargs[name] = _gettag(e, 'itunes:' + name)
    kwargs['duration'] = _gettag(e, 'itunes:duration', _to_timedelta)
    kwargs['keywords'] = _gettag(e, 'itunes:keywords', _to_wordlist)
    kwargs['order'] = _gettag(e, 'itunes:order', lambda e: int(e.text))
    return Episode(**kwargs)


class Podcast(mopidy.models.ImmutableObject):

    Image = namedtuple('Image', 'url title link width height description')

    # standard RSS tags
    title = None
    link = None
    description = None
    language = None
    copyright = None
    pubdate = None
    image = None

    # iTunes tags
    author = None
    complete = None
    explicit = None
    subtitle = None
    summary = None
    keywords = frozenset()
    category = None  # TODO: sub-categories

    # tuple of episodes/items
    episodes = tuple()

    def __init__(self, *args, **kwargs):
        self.__dict__['episodes'] = tuple(
            kwargs.pop('episodes', None) or []
        )
        self.__dict__['keywords'] = frozenset(
            kwargs.pop('keywords', None) or []
        )
        super(Podcast, self).__init__(*args, **kwargs)

    @classmethod
    def parse(cls, source):
        import xml.etree.ElementTree as ET
        channel = ET.parse(source).find('channel')

        kwargs = {}
        for name in ('title', 'link', 'description', 'language', 'copyright'):
            kwargs[name] = _gettag(channel, name)
        kwargs['pubdate'] = _gettag(channel, 'pubDate', _to_datetime)
        kwargs['image'] = _gettag(channel, 'image', _to_image)
        for name in ('author', 'complete', 'explicit', 'subtitle', 'summary'):
            kwargs[name] = _gettag(channel, 'itunes:' + name)
        kwargs['keywords'] = _gettag(channel, 'itunes:keywords', _to_wordlist)
        kwargs['category'] = _gettag(channel, 'itunes:category',
                                     lambda e: e.get('text'))
        kwargs['episodes'] = _gettags(channel, 'item', _to_episode)
        return cls(**kwargs)


class Episode(mopidy.models.ImmutableObject):

    Enclosure = namedtuple('Enclosure', 'url length type')

    # standard RSS tags
    title = None
    link = None
    description = None
    guid = None
    pubdate = None
    enclosure = None

    # iTunes tags
    author = None
    block = None
    explicit = None
    subtitle = None
    summary = None
    duration = None
    keywords = frozenset()
    order = None

    def __init__(self, *args, **kwargs):
        self.__dict__['keywords'] = frozenset(
            kwargs.pop('keywords', None) or []
        )
        super(Episode, self).__init__(*args, **kwargs)


class Ref(mopidy.models.Ref):

    PODCAST = 'podcast'
    """Constant used for comparison with the :attr:`type` field."""

    EPISODE = 'episode'
    """Constant used for comparison with the :attr:`type` field."""

    @classmethod
    def podcast(cls, **kwargs):
        """Create a :class:`Ref` with ``type`` :attr:`PODCAST`."""
        if 'uri' in kwargs and '#' in kwargs['uri']:
            raise ValueError('Podcast URI with fragment: %s' % kwargs['uri'])
        kwargs['type'] = Ref.PODCAST
        return cls(**kwargs)

    @classmethod
    def episode(cls, **kwargs):
        """Create a :class:`Ref` with ``type`` :attr:`EPISODE`."""
        if 'uri' in kwargs and '#' not in kwargs['uri']:
            raise ValueError('Episode URI needs fragment: %s' % kwargs['uri'])
        kwargs['type'] = Ref.EPISODE
        return cls(**kwargs)
