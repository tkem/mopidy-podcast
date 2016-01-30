from __future__ import unicode_literals

import pytest

from mopidy_podcast import feeds


def test_no_default_root_directory(library):
    assert library.root_directory is None  # TODO


@pytest.mark.parametrize('filename', ['directory.xml', 'rssfeed.xml'])
def test_browse(config, library, filename, abspath):
    feed = feeds.parse(abspath(filename))
    newest_first = config['podcast']['browse_order'] == 'desc'
    assert library.browse(feed.uri) == list(feed.items(newest_first))
    assert feed.uri in library.backend.feeds


@pytest.mark.parametrize('filename', ['rssfeed.xml'])
def test_get_images(library, filename, abspath):
    feed = feeds.parse(abspath(filename))
    for uri, images in feed.images():
        assert library.get_images([uri]) == {uri: images}
    images = {uri: images for uri, images in feed.images()}
    assert library.get_images(list(images)) == images
    assert feed.uri in library.backend.feeds


@pytest.mark.parametrize('filename', ['rssfeed.xml'])
def test_lookup(config, library, filename, abspath):
    feed = feeds.parse(abspath(filename))
    for track in feed.tracks():
        assert library.lookup(track.uri) == [track]
    newest_first = config['podcast']['lookup_order'] == 'desc'
    assert library.lookup(feed.uri) == list(feed.tracks(newest_first))
    assert feed.uri in library.backend.feeds


@pytest.mark.parametrize('filename', ['rssfeed.xml'])
def test_refresh(library, filename, abspath):
    feed = feeds.parse(abspath(filename))
    tracks = library.lookup(feed.uri)
    assert feed.uri in library.backend.feeds
    library.refresh(tracks[0].uri)
    assert feed.uri not in library.backend.feeds
    library.lookup(tracks[0].uri)
    assert feed.uri in library.backend.feeds
    library.refresh()
    assert not library.backend.feeds
