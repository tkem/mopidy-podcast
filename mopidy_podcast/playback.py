from __future__ import unicode_literals

import logging

from mopidy import backend

logger = logging.getLogger(__name__)


class PodcastPlaybackProvider(backend.PlaybackProvider):

    def change_track(self, track):
        track = track.copy(uri=self.backend.library.getstream(track.uri))
        return super(PodcastPlaybackProvider, self).change_track(track)
