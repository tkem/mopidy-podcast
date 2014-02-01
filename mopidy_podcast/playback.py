from __future__ import unicode_literals

import logging

from mopidy import backend

from .uritools import urisplit

logger = logging.getLogger(__name__)


class PodcastPlaybackProvider(backend.PlaybackProvider):

    def change_track(self, track):
        track = track.copy(uri=urisplit(track.uri).getpath().lstrip('/'))
        return super(PodcastPlaybackProvider, self).change_track(track)
