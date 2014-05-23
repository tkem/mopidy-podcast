from __future__ import unicode_literals

import logging
import pykka
import threading

from mopidy import backend

from . import Extension
from .controller import PodcastDirectoryController
from .library import PodcastLibraryProvider
from .playback import PodcastPlaybackProvider

logger = logging.getLogger(__name__)


class PodcastBackend(pykka.ThreadingActor, backend.Backend):

    uri_schemes = ['podcast']

    directories = []

    def __init__(self, config, audio):
        super(PodcastBackend, self).__init__()
        directories = [cls(config) for cls in self.directories]
        logger.info('Starting %s directories: %s', Extension.dist_name,
                    ', '.join(d.__class__.__name__ for d in directories))
        self.directory = PodcastDirectoryController(directories)
        self.library = PodcastLibraryProvider(config, backend=self)
        self.playback = PodcastPlaybackProvider(audio=audio, backend=self)
        self.lock = threading.RLock()

        interval = config[Extension.ext_name]['update_interval']

        def update():
            logger.info('Refreshing %s directories', Extension.dist_name)
            self.directory.refresh(async=True)
            self.timer = self._timer(interval, update)
        update()

    def on_stop(self):
        with self.lock:
            self.timer.cancel()
        logger.info('Stopping %s directories', Extension.dist_name)
        self.directory.stop()
        logger.debug('Stoppped %s directories', Extension.dist_name)

    def _timer(self, interval, func):
        if not interval or not func:
            return None
        with self.lock:
            if self.actor_stopped.is_set():
                return None
            timer = threading.Timer(interval, func)
            timer.start()
            return timer
