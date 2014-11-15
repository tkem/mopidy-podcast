from __future__ import unicode_literals

import uritools

from mopidy import backend


class PodcastPlaybackProvider(backend.PlaybackProvider):

    def change_track(self, track):
        track = track.copy(uri=uritools.uridefrag(track.uri).fragment)
        return super(PodcastPlaybackProvider, self).change_track(track)
