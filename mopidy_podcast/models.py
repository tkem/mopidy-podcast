from __future__ import unicode_literals

import collections
import datetime
import email.utils
import re

import mopidy.models

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


def _to_datetime(e):
    try:
        timestamp = email.utils.mktime_tz(email.utils.parsedate_tz(e.text))
    except AttributeError:
        return None
    except TypeError:
        return None
    return datetime.datetime.fromtimestamp(timestamp)


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


def _to_wordlist(e):
    return [s.strip() for s in e.text.split(',')] if e.text else None


def _to_image(e):
    return Podcast.Image(
        e.get('url'), e.get('title'), e.get('link'),
        e.get('width'), e.get('height'), e.get('description')
    )


def _to_enclosure(e):
    return Episode.Enclosure(e.get('url'), e.get('length'), e.get('type'))


def _by_pubdate(episode):
    return episode.pubdate if episode.pubdate else datetime.datetime.min


def _to_episode(e):
    kwargs = {}
    for name in ('title', 'link', 'description', 'guid'):
        kwargs[name] = _gettag(e, name)
    kwargs['pubdate'] = _gettag(e, 'pubDate', _to_datetime)
    kwargs['enclosure'] = _gettag(e, 'enclosure', _to_enclosure)
    for name in ('author', 'explicit', 'subtitle'):
        kwargs[name] = _gettag(e, 'itunes:' + name)
    # TODO: <itunes:summary> vs. <description>
    kwargs['duration'] = _gettag(e, 'itunes:duration', _to_timedelta)
    kwargs['keywords'] = _gettag(e, 'itunes:keywords', _to_wordlist)
    kwargs['order'] = _gettag(e, 'itunes:order', lambda e: int(e.text))
    return Episode(**kwargs)


class Podcast(mopidy.models.ImmutableObject):
    """Mopidy model type to represent a podcast."""

    Image = collections.namedtuple(
        'Image', 'url title link width height description'
    )
    """A :class:`collections.namedtuple` subclass to represent a podcast's
    image.

    """

    # standard RSS tags

    title = None
    """The podcast's title."""

    link = None
    """The URL of the HTML website corresponding to the podcast."""

    description = None
    """A description of the podcast."""

    language = None
    """The podcast's ISO two-letter language code."""

    copyright = None
    """The podcast's copyright notice."""

    pubdate = None
    """The podcast's publication date as a :class:`datetime.datetime`."""

    image = None
    """An image to be displayed with the podcast as an instance of
    :class:`Image`.

    """

    # iTunes tags

    author = None
    """The podcast author's name."""

    complete = None
    """Indicates completion of the podcast."""

    explicit = None
    """Indicates whether the podcast contains explicit material."""

    subtitle = None
    """A short description of the podcast."""

    keywords = frozenset()
    """A list of keywords associated with the podcast."""

    category = None
    """The top-level category of the podcast."""

    # episodes

    episodes = tuple()
    """The podcast's episodes as a read-only :class:`tuple`.

    By default, i.e. when using :meth:`Podcast.parse` to create a
    :class:`Podcast`, a podcast's episodes are sorted by descending
    :attr:`pubdate`.

    """

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
        """Parse an RSS feed from a file-like `source` object into a
        :class:`Podcast`.

        """
        import xml.etree.ElementTree as ET
        channel = ET.parse(source).find('channel')

        kwargs = {}
        for name in ('title', 'link', 'description', 'language', 'copyright'):
            kwargs[name] = _gettag(channel, name)
        kwargs['pubdate'] = _gettag(channel, 'pubDate', _to_datetime)
        kwargs['image'] = _gettag(channel, 'image', _to_image)
        for name in ('author', 'complete', 'explicit', 'subtitle'):
            kwargs[name] = _gettag(channel, 'itunes:' + name)
        # TODO: <itunes:summary> vs. <description>
        kwargs['keywords'] = _gettag(channel, 'itunes:keywords', _to_wordlist)
        kwargs['category'] = _gettag(channel, 'itunes:category', _to_category)
        kwargs['episodes'] = [_to_episode(e) for e in channel.iter(tag='item')]
        kwargs['episodes'].sort(key=_by_pubdate, reverse=True)
        return cls(**kwargs)


class Episode(mopidy.models.ImmutableObject):
    """Mopidy model type to represent a podcast episode."""

    Enclosure = collections.namedtuple('Enclosure', 'url length type')
    """A :class:`collections.namedtuple` subclass to represent an
    episode's enclosure.

    """

    # standard RSS tags

    title = None
    """The episode's title."""

    link = None
    """The URL of the HTML website corresponding to the episode."""

    description = None
    """A description of the episode."""

    guid = None
    """A string that uniquely identifies the episode."""

    pubdate = None
    """The episode's publication date as a :class:`datetime.datetime`."""

    enclosure = None
    """The media object, e.g. the audio stream, attached to the episode as
    an instance of :class:`Enclosure`.

    """

    # iTunes tags

    author = None
    """The episode author's name."""

    explicit = None
    """Indicates whether the episode contains explicit material."""

    subtitle = None
    """A short description of the episode."""

    duration = None
    """The episode's duration as a :class:`datetime.timedelta`."""

    keywords = frozenset()
    """A list of keywords associated with the episode."""

    order = None
    """Can be used to override the default ordering of episodes."""

    def __init__(self, *args, **kwargs):
        self.__dict__['keywords'] = frozenset(
            kwargs.pop('keywords', None) or []
        )
        super(Episode, self).__init__(*args, **kwargs)


class Ref(mopidy.models.Ref):
    """Extends :class:`mopidy.models.Ref` to provide factory methods and
    type constants for :class:`Podcast` and :class:`Episode`.

    """

    PODCAST = 'podcast'
    """Constant used for comparison with the :attr:`type` field."""

    EPISODE = 'episode'
    """Constant used for comparison with the :attr:`type` field."""

    @classmethod
    def podcast(cls, **kwargs):
        """Create a :class:`Ref` with :attr:`type` :attr:`PODCAST`.

        A :const:`uri` keyword argument *MUST* be the podcast's RSS
        feed URL, and *MUST NOT* contain a fragment component.

        """
        if 'uri' in kwargs and '#' in kwargs['uri']:
            raise ValueError('Invalid podcast URI: %s' % kwargs['uri'])
        kwargs['type'] = Ref.PODCAST
        return cls(**kwargs)

    @classmethod
    def episode(cls, **kwargs):
        """Create a :class:`Ref` with :attr:`type` :attr:`EPISODE`.

        A :const:`uri` keyword argument *MUST* be the podcast's RSS
        feed URL with the episode's enclosure URL appended as the
        fragment.

        """
        if 'uri' in kwargs and '#' not in kwargs['uri']:
            raise ValueError('Invalid episode URI: %s' % kwargs['uri'])
        kwargs['type'] = Ref.EPISODE
        return cls(**kwargs)
