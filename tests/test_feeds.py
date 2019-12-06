import uritools

import pytest
from mopidy_podcast import feeds


@pytest.mark.parametrize(
    "filename,expected",
    [("directory.xml", feeds.OpmlFeed), ("rssfeed.xml", feeds.RssFeed)],
)
def test_parse(abspath, filename, expected):
    path = abspath(filename)
    feed = feeds.parse(path)
    assert isinstance(feed, expected)
    assert feed.uri == uritools.uricompose("podcast+file", "", path)
