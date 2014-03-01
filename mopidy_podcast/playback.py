from __future__ import unicode_literals

from mopidy import backend


class PodcastPlaybackProvider(backend.PlaybackProvider):

    def change_track(self, track):
        track = track.copy(uri=self.backend.get_stream_url(track.uri))
        return super(PodcastPlaybackProvider, self).change_track(track)
