from __future__ import unicode_literals

import mopidy.models


class Image(mopidy.models.ImmutableObject):
    """Mopidy model type to represent a podcast's image."""

    uri = None
    """The image's URI."""

    title = None
    """The image's title."""

    width = None
    """The image's width in pixels."""

    height = None
    """The image's height in pixels."""


class Enclosure(mopidy.models.ImmutableObject):
    """Mopidy model type to represent an episode's media object."""

    uri = None
    """The URI of the media object."""

    length = None
    """The enclosure's file size in bytes."""

    type = None
    """The MIME type of the enclosure, e.g. :const:`audio/mpeg`."""


class Podcast(mopidy.models.ImmutableObject):
    """Mopidy model type to represent a podcast."""

    uri = None
    """The podcast URI.

    For podcasts distributed as RSS feeds, the podcast URI is the URL
    from which the RSS feed can be retrieved.

    To distinguish between podcast and episode URIs, the podcast URI
    *MUST NOT* contain a fragment identifier.

    """

    title = None
    """The podcast's title."""

    link = None
    """The URL of the HTML website corresponding to the podcast."""

    copyright = None
    """The podcast's copyright notice."""

    language = None
    """The podcast's ISO two-letter language code."""

    pubdate = None
    """The podcast's publication date and time as an instance of
    :class:`datetime.datetime`.

    """

    author = None
    """The podcast's author's name."""

    block = None
    """Prevent a podcast from appearing in the directory."""

    category = None
    """The main category of the podcast."""

    image = None
    """An image to be displayed with the podcast as an instance of
    :class:`Image`.

    """

    explicit = None
    """Indicates whether the podcast contains explicit material."""

    complete = None
    """Indicates completion of the podcast."""

    newfeedurl = None
    """Used to inform of new feed URL location."""

    subtitle = None
    """A short description of the podcast."""

    summary = None
    """A description of the podcast, up to 4000 characters long."""

    episodes = tuple()
    """The podcast's episodes as a read-only :class:`tuple` of
    :class:`Episode` instances.

    """

    def __init__(self, *args, **kwargs):
        self.__dict__['episodes'] = tuple(
            kwargs.pop('episodes', None) or []
        )
        super(Podcast, self).__init__(*args, **kwargs)


class Episode(mopidy.models.ImmutableObject):
    """Mopidy model type to represent a podcast episode."""

    uri = None
    """The episode URI.

    If the episode contains an enclosure, the episode URI *MUST*
    consist of the associated podcast URI with the enclosure URL
    appended as a fragment identifier.

    """

    title = None
    """The episode's title."""

    guid = None
    """A string that uniquely identifies the episode."""

    pubdate = None
    """The episode's publication date and time as an instance of
    :class:`datetime.datetime`.

    """

    author = None
    """The episode's author's name."""

    block = None
    """Prevent an episode from appearing in the directory."""

    image = None
    """An image to be displayed with the episode as an instance of
    :class:`Image`.

    """

    duration = None
    """The episode's duration as an instance of
    :class:`datetime.timedelta`.

    """

    explicit = None
    """Indicates whether the episode contains explicit material."""

    order = None
    """Overrides the default ordering of episodes."""

    subtitle = None
    """A short description of the episode."""

    summary = None
    """A description of the episode, up to 4000 characters long."""

    enclosure = None
    """The media object, e.g. the audio stream, attached to the episode as
    an instance of :class:`Enclosure`.

    """


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
