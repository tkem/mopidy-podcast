from mopidy import models

import pytest
from mopidy_podcast import feeds

XML = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head>
    <title>example.opml</title>
    <dateCreated>Tue, 02 Mar 2016 12:01:00 GMT</dateCreated>
    <dateModified>Tue, 02 Mar 2016 12:01:00 GMT</dateModified>
  </head>
  <body>
    <outline text="Podcast" type="rss"
             xmlUrl="http://example.com/podcast1.rss"/>
    <outline title="Podcast" type="rss"
             xmlUrl="http://example.com/podcast2.xml"/>
    <outline text="Description" title="Podcast" type="rss"
             xmlUrl="http://example.com/podcast3"/>
    <outline text="Directory" type="include"
             url="http://example.com/directory1"/>
    <outline text="Directory" type="link"
             url="http://example.com/directory2.opml"/>
    <outline text="Podcast" type="link"
             url="http://example.com/podcast4.xml"/>
    <!-- some OPML generators use uppercase "URL" attribute -->
    <outline text="PODCAST" type="link"
             URL="http://example.com/podcast5.xml"/>
    <outline text="Foo" type="bar"/>
    <outline text="Foo"/>
  </body>
</opml>"""


@pytest.fixture
def opml():
    from io import StringIO

    class StringSource(StringIO):
        def geturl(self):
            return "http://example.com/example.opml"

    return StringSource(XML)


def test_items(opml):
    feed = feeds.parse(opml)
    assert list(feed.items()) == [
        models.Ref.album(
            uri="podcast+http://example.com/podcast1.rss", name="Podcast"
        ),
        models.Ref.album(
            uri="podcast+http://example.com/podcast2.xml", name="Podcast"
        ),
        models.Ref.album(
            uri="podcast+http://example.com/podcast3", name="Podcast"
        ),
        models.Ref.directory(
            uri="podcast+http://example.com/directory1", name="Directory"
        ),
        models.Ref.directory(
            uri="podcast+http://example.com/directory2.opml", name="Directory"
        ),
        models.Ref.album(
            uri="podcast+http://example.com/podcast4.xml", name="Podcast"
        ),
        models.Ref.album(
            uri="podcast+http://example.com/podcast5.xml", name="PODCAST"
        ),
    ]


def test_tracks(opml):
    feed = feeds.parse(opml)
    assert list(feed.tracks()) == []


def test_images(opml):
    feed = feeds.parse(opml)
    assert dict(feed.images()) == {}
