import pytest
from mopidy_podcast import feeds


@pytest.mark.parametrize("filename", ["rssfeed.xml"])
def test_translate_uri(playback, filename, abspath):
    feed = feeds.parse(abspath(filename))
    for track in feed.tracks():
        assert playback.translate_uri(track.uri) is not None
    assert playback.translate_uri(feed.uri + "#n/a") is None
    assert playback.translate_uri(feed.uri) is None


def test_translate_empty_uri(playback):
    assert playback.translate_uri("") is None
