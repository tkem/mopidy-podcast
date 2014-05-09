from __future__ import unicode_literals

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


def _to_isoformat(e):
    try:
        t = email.utils.mktime_tz(email.utils.parsedate_tz(e.text))
    except AttributeError:
        return None
    except TypeError:
        return None
    return datetime.datetime.utcfromtimestamp(t).isoformat() + 'Z'


def _to_milliseconds(e):
    try:
        groups = _DURATION_RE.match(e.text).groupdict('0')
    except AttributeError:
        return None
    except TypeError:
        return None
    d = datetime.timedelta(**{k: int(v) for k, v in groups.items()})
    return int(d.total_seconds() * 1000)


def _to_category(e):
    return e.get('text')


def _to_wordlist(e):
    return [s.strip() for s in e.text.split(',')] if e.text else None


def _to_image(e):
    kwargs = {}
    # handle both RSS and itunes images
    kwargs['uri'] = e.get('href', _gettag(e, 'url'))
    # these are only valid for RSS images
    for name in ('title', 'link', 'width', 'height', 'description'):
        kwargs[name] = _gettag(e, name)
    return Image(**kwargs)


def _to_enclosure(e):
    return Enclosure(
        uri=e.get('url'),
        length=e.get('length'),
        type=e.get('type')
    )


def _to_episode(e, feedurl):
    kwargs = {}
    # standard RSS tags
    for name in ('title', 'link', 'description', 'guid'):
        kwargs[name] = _gettag(e, name)
    kwargs['pubdate'] = _gettag(e, 'pubDate', _to_isoformat)
    kwargs['enclosure'] = _gettag(e, 'enclosure', _to_enclosure)
    # itunes tags
    for name in ('author', 'block', 'explicit', 'subtitle'):
        kwargs[name] = _gettag(e, 'itunes:' + name)
    kwargs['image'] = _gettag(e, 'itunes:image', _to_image)
    kwargs['duration'] = _gettag(e, 'itunes:duration', _to_milliseconds)
    kwargs['order'] = _gettag(e, 'itunes:order', lambda e: int(e.text))
    kwargs['keywords'] = _gettag(e, 'itunes:keywords', _to_wordlist)
    # add uri if valid
    if feedurl and kwargs['enclosure'] and kwargs['enclosure'].uri:
        kwargs['uri'] = feedurl + '#' + kwargs['enclosure'].uri
    return Episode(**kwargs)


def _by_pubdate(episode):
    return episode.pubdate or ''


class Image(mopidy.models.ImmutableObject):
    """Mopidy model type to represent a podcast's image."""

    uri = None
    """The image's URI."""

    title = None
    """The image's title."""

    link = None
    """The URL of the site the image links to."""

    width = None
    """The image's width in pixels."""

    height = None
    """The image's height in pixels."""

    description = None
    """A description of the image or the site it links to."""


class Enclosure(mopidy.models.ImmutableObject):
    """Mopidy model type to represent an episode's media object."""

    uri = None
    """The URI of the media object."""

    length = None
    """The size of the media object in bytes."""

    type = None
    """The MIME type of the media object, e.g. `audio/mpeg`."""


class Podcast(mopidy.models.ImmutableObject):
    """Mopidy model type to represent a podcast."""

    uri = None
    """The podcast URI.

    To distinguish between podcast and episode URIs, the podcast URI
    *MUST NOT* contain a fragment identifier.  For podcasts
    distributed as RSS feeds, this is the URL from which the RSS feed
    can be retrieved.

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
    """The podcast's publication date and time in ISO 8601 format."""

    image = None
    """An image to be displayed with the podcast as an instance of
    :class:`Image`.

    """

    # iTunes tags

    author = None
    """The podcast author's name."""

    block = None
    """Prevent a podcast from appearing."""

    # TODO: sub-categories
    category = None
    """The top-level category of the podcast."""

    explicit = None
    """Indicates whether the podcast contains explicit material."""

    complete = None
    """Indicates completion of the podcast."""

    newfeedurl = None
    """Used to inform of new feed URL location."""

    subtitle = None
    """A short description of the podcast."""

    keywords = frozenset()
    """A set of keywords to associate with the podcast."""

    # episodes

    episodes = tuple()
    """The podcast's episodes as a read-only :class:`tuple` of
    :class:`Episode` instances.

    When using :meth:`Podcast.parse` to create a :class:`Podcast`, a
    podcast's episodes are sorted by descending :attr:`pubdate`.

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
    def parse(cls, source, uri=None):
        """Parse an RSS feed from a file-like `source` object into a
        :class:`Podcast`.

        """
        import xml.etree.ElementTree as ET
        channel = ET.parse(source).find('channel')

        kwargs = {}
        # strip superfluous fragment from feedurl
        kwargs['uri'] = uri.partition('#')[0] if uri else None
        # standard RSS tags
        for name in ('title', 'link', 'description', 'language', 'copyright'):
            kwargs[name] = _gettag(channel, name)
        kwargs['pubdate'] = _gettag(channel, 'pubDate', _to_isoformat)
        kwargs['image'] = _gettag(channel, 'image', _to_image)
        # itunes tags
        for name in ('author', 'block', 'complete', 'explicit', 'subtitle'):
            kwargs[name] = _gettag(channel, 'itunes:' + name)
        # TBD: prefer itunes image over RSS image?
        if not kwargs['image']:
            kwargs['image'] = _gettag(channel, 'itunes:image', _to_image)
        kwargs['category'] = _gettag(channel, 'itunes:category', _to_category)
        kwargs['keywords'] = _gettag(channel, 'itunes:keywords', _to_wordlist)
        kwargs['newfeedurl'] = _gettag(channel, 'itunes:new-feed-url')

        # episodes sorted by pubdate
        episodes = []
        for item in channel.iter(tag='item'):
            # TODO: filter by media type?
            episodes.append(_to_episode(item, kwargs['uri']))
        kwargs['episodes'] = sorted(episodes, key=_by_pubdate, reverse=True)
        return cls(**kwargs)


class Episode(mopidy.models.ImmutableObject):
    """Mopidy model type to represent a podcast episode."""

    uri = None
    """The episode URI.

    If the episode contains an enclosure, the episode URI *MUST* be
    the associated podcast URI with the enclosure URL appended as a
    fragment identifier.

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
    """The episode's publication date and time in ISO 8601 format."""

    enclosure = None
    """The media object, e.g. the audio stream, attached to the episode as
    an instance of :class:`Enclosure`.

    """

    # iTunes tags

    author = None
    """The episode author's name."""

    block = None
    """Prevent an episode from appearing."""

    image = None
    """An image to be displayed with the episode as an instance of
    :class:`Image`.

    """

    duration = None
    """The episode's duration in milliseconds."""

    explicit = None
    """Indicates whether the episode contains explicit material."""

    order = None
    """Overrides the default ordering of episodes."""

    subtitle = None
    """A short description of the episode."""

    keywords = frozenset()
    """A list of keywords associated with the episode."""

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
        """Create a :class:`Ref` with :attr:`type` :attr:`PODCAST`."""
        kwargs['type'] = Ref.PODCAST
        return cls(**kwargs)

    @classmethod
    def episode(cls, **kwargs):
        """Create a :class:`Ref` with :attr:`type` :attr:`EPISODE`."""
        kwargs['type'] = Ref.EPISODE
        return cls(**kwargs)
