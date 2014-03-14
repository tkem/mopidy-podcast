from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend

from . import Extension
from .directory import PodcastDirectoryController
from .library import PodcastLibraryProvider
from .playback import PodcastPlaybackProvider
from .uritools import uridefrag

logger = logging.getLogger(__name__)


class PodcastBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = ['podcast']

    registry = None

    name = Extension.ext_name

    def __init__(self, config, audio):
        super(PodcastBackend, self).__init__()
        directories = self._directories(config[self.name]['directories'])

        self.config = config
        self.cache = self._cache(**config[self.name])
        self.timeout = config[self.name]['timeout']
        self.max_episodes = config[self.name]['max_episodes']
        self.directory = PodcastDirectoryController(self, directories)
        self.library = PodcastLibraryProvider(backend=self)
        self.playback = PodcastPlaybackProvider(audio=audio, backend=self)

        update_interval = config[self.name]['update_interval']

        def update():
            logger.info('Updating %s directories', Extension.dist_name)
            self.directory.refresh(async=True)
            if not self.actor_stopped.is_set():
                self.timer = self._timer(update_interval, update)
            else:
                logger.debug('%s stopped during update', Extension.dist_name)

        self.timer = self._timer(update_interval, update)

    def on_stop(self):
        self.timer.cancel()
        self.directory.stop()

    def get_stream_url(self, uri):
        return uridefrag(uri).fragment

    def _cache(self, cache_size=0, cache_ttl=0, **kwargs):
        from .lrucache import LRUCache
        if cache_size and cache_ttl:
            return LRUCache(maxsize=cache_size, ttl=cache_ttl)
        else:
            return None

    def _directories(self, names):
        regdirs = {d.name: d for d in self.registry['podcast:directory']}
        classes = []
        for name in names:
            if name in regdirs:
                classes.append(regdirs[name])
            else:
                logger.warn('Podcast directory %s not found', name)
        return classes

    def _timer(self, interval, func):
        from threading import Timer
        timer = Timer(interval, func)
        timer.start()
        return timer
