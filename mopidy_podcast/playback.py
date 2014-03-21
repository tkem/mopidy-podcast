from __future__ import unicode_literals

from mopidy import backend

from .uritools import uridefrag


class PodcastPlaybackProvider(backend.PlaybackProvider):

    def change_track(self, track):
        track = track.copy(uri=uridefrag(track.uri).fragment)
        return super(PodcastPlaybackProvider, self).change_track(track)
