import contextlib
import logging

import cachetools
import pykka
from mopidy import backend

from . import Extension, feeds
from .library import PodcastLibraryProvider
from .playback import PodcastPlaybackProvider

logger = logging.getLogger(__name__)


class PodcastFeedCache(cachetools.TTLCache):

    pykka_traversable = True

    def __init__(self, config):
        super().__init__(
            maxsize=config[Extension.ext_name]["cache_size"],
            ttl=config[Extension.ext_name]["cache_ttl"],
        )
        self.__opener = Extension.get_url_opener(config)
        self.__timeout = config[Extension.ext_name]["timeout"]

    def __missing__(self, uri):
        ext_name, _, feedurl = uri.partition("+")
        assert ext_name == Extension.ext_name
        f = self.__opener.open(feedurl, timeout=self.__timeout)
        with contextlib.closing(f) as source:
            feed = feeds.parse(source)
        # do not cache local URIs so updates are available immediately
        if not feedurl.startswith("file:"):
            self[uri] = feed
        return feed


class PodcastBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = ["podcast", "podcast+file", "podcast+http", "podcast+https"]

    def __init__(self, config, audio):
        super().__init__()
        self.feeds = PodcastFeedCache(config)
        self.library = PodcastLibraryProvider(config, backend=self)
        self.playback = PodcastPlaybackProvider(audio, backend=self)
