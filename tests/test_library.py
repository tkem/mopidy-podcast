import pytest
from mopidy_podcast import feeds


def test_root_directory(library):
    assert library.root_directory is not None
    assert library.root_directory.name == "Podcasts"
    assert library.root_directory.uri.endswith("Podcasts.opml")


@pytest.mark.parametrize("filename", ["directory.xml", "rssfeed.xml"])
def test_browse(config, library, filename, abspath):
    feed = feeds.parse(abspath(filename))
    newest_first = config["podcast"]["browse_order"] == "desc"
    assert library.browse(feed.uri) == list(feed.items(newest_first))


@pytest.mark.parametrize("uri,expected", [(None, []), ("podcast+file:///", [])])
def test_browse_error(library, uri, expected):
    if isinstance(expected, type):
        with pytest.raises(expected):
            library.browse(uri)
    else:
        assert library.browse(uri) == expected


@pytest.mark.parametrize("filename", ["rssfeed.xml"])
def test_get_images(library, filename, abspath):
    feed = feeds.parse(abspath(filename))
    for uri, images in feed.images():
        assert library.get_images([uri]) == {uri: images}
    images = {uri: images for uri, images in feed.images()}
    assert library.get_images(list(images)) == images


@pytest.mark.parametrize(
    "uris,expected", [(None, TypeError), ("podcast+file:///", {})]
)
def test_get_images_error(library, uris, expected):
    if isinstance(expected, type):
        with pytest.raises(expected):
            library.get_images(uris)
    else:
        assert library.get_images(uris) == expected


@pytest.mark.parametrize("filename", ["rssfeed.xml"])
def test_lookup(config, library, filename, abspath):
    feed = feeds.parse(abspath(filename))
    for track in feed.tracks():
        assert library.lookup(track.uri) == [track]
    newest_first = config["podcast"]["lookup_order"] == "desc"
    assert library.lookup(feed.uri) == list(feed.tracks(newest_first))


@pytest.mark.parametrize("uri,expected", [(None, []), ("podcast+file:///", [])])
def test_lookup_error(library, uri, expected):
    if isinstance(expected, type):
        with pytest.raises(expected):
            library.lookup(uri)
    else:
        assert library.lookup(uri) == expected


@pytest.mark.parametrize("filename", ["rssfeed.xml"])
def test_refresh(library, filename, abspath):
    feed = feeds.parse(abspath(filename))
    tracks = library.lookup(feed.uri)
    assert feed.uri not in library.backend.feeds  # local feeds not cached!
    library.backend.feeds[feed.uri] = feed
    assert feed.uri in library.backend.feeds
    library.refresh(tracks[0].uri)
    assert feed.uri not in library.backend.feeds
    library.backend.feeds[feed.uri] = feed
    assert library.backend.feeds
    library.refresh()
    assert not library.backend.feeds
