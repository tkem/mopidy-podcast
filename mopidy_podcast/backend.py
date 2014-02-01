from __future__ import unicode_literals

import logging
import pykka

from mopidy import backend

from .library import PodcastLibraryProvider
from .playback import PodcastPlaybackProvider

logger = logging.getLogger(__name__)


class PodcastBackend(pykka.ThreadingActor, backend.Backend):

    URI_SCHEME = 'podcast'

    uri_schemes = [URI_SCHEME]

    def __init__(self, config, audio):
        super(PodcastBackend, self).__init__()
        self.config = config
        self.library = PodcastLibraryProvider(backend=self)
        self.playback = PodcastPlaybackProvider(audio=audio, backend=self)

    def getconfig(self, name):
        return self.config[self.URI_SCHEME][name]
