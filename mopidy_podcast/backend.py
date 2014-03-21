from __future__ import unicode_literals

import logging
import pykka
import threading

from mopidy import backend

from . import Extension
from .controller import PodcastDirectoryController
from .feeds import FeedsDirectory
from .library import PodcastLibraryProvider
from .playback import PodcastPlaybackProvider

logger = logging.getLogger(__name__)


class PodcastBackend(pykka.ThreadingActor, backend.Backend):

    # TODO: new uri scheme:
    # - podcast://dirname/...
    # - podcast+http://...
    # - podcast+https://...
    # blocked by https://github.com/mopidy/mopidy/issues/708
    uri_schemes = ['podcast']

    lock = threading.RLock()
    name = Extension.ext_name
    registry = None

    def __init__(self, config, audio):
        super(PodcastBackend, self).__init__()
        classes = [FeedsDirectory] if config[self.name]['feeds'] else []
        classes.extend(self.registry[self.name + ':directory'])
        timeout = config[self.name]['timeout']

        self.config = config
        self.directory = PodcastDirectoryController(config, timeout, classes)
        self.library = PodcastLibraryProvider(backend=self)
        self.playback = PodcastPlaybackProvider(audio=audio, backend=self)

        def update():
            logger.info('Updating %s directories', Extension.dist_name)
            self.directory.update(async=True)
            with self.lock:
                interval = config[self.name]['update_interval']
                self.timer = self._timer(interval, update)
        update()

    def on_stop(self):
        if not self.actor_stopped.is_set():
            logger.error('%r stopped, but event not set', self)
        with self.lock:
            self.timer.cancel()
        self.directory.stop()

    def _timer(self, interval, func):
        if self.actor_stopped.is_set():
            return None
        if not interval:
            return None
        timer = threading.Timer(interval, func)
        timer.start()
        return timer
