from mopidy import models

import pytest
from mopidy_podcast import feeds

XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">
<channel>
<title>All About Everything</title>
<link>http://www.example.com/everything/index.html</link>
<language>en-us</language>
<copyright>&#x2117; &amp; &#xA9; 2014 John Doe &amp; Family</copyright>
<itunes:author>John Doe</itunes:author>
<description>All About Everything is a show about everything.</description>
<itunes:image href="http://example.com/everything/Podcast.jpg" />
<itunes:category text="Technology" />
<item>
<title>Shake Shake Shake Your Spices</title>
<itunes:image href="http://example.com/everything/Episode3.jpg" />
<enclosure url="http://example.com/everything/Episode3.m4a"
           length="8727310" type="audio/x-m4a" />
<guid>episode3</guid>
<pubDate>Wed, 15 Jun 2014 19:00:00 GMT</pubDate>
<itunes:duration>7:04</itunes:duration>
</item>
<item>
<title>Socket Wrench Shootout</title>
<itunes:author>Jane Doe</itunes:author>
<itunes:image href="http://example.com/everything/Episode2.jpg" />
<enclosure url="http://example.com/everything/Episode2.mp3"
           length="5650889" type="audio/mpeg" />
<guid>episode2</guid>
<pubDate>Wed, 8 Jun 2014 19:00:00 GMT</pubDate>
<itunes:duration>4:34</itunes:duration>
</item>
<item>
<title>Red, Whine, &amp; Blue</title>
<itunes:author>Various</itunes:author>
<enclosure url="http://example.com/everything/Episode1.mp3"
           length="498537" type="audio/mpeg" />
<pubDate>Wed, 1 Jun 2014 19:00:00 GMT</pubDate>
<itunes:duration>3:59</itunes:duration>
</item>
</channel>
</rss>"""


@pytest.fixture
def rss():
    from io import StringIO

    class StringSource(StringIO):
        def geturl(self):
            return "http://www.example.com/everything.xml"

    return feeds.parse(StringSource(XML))


@pytest.fixture
def album():
    return models.Album(
        uri="podcast+http://www.example.com/everything.xml",
        name="All About Everything",
        artists=[models.Artist(name="John Doe")],
        num_tracks=3,
    )


@pytest.fixture
def tracks(album):
    return [
        models.Track(
            uri="podcast+http://www.example.com/everything.xml#episode3",
            name="Shake Shake Shake Your Spices",
            artists=[models.Artist(name="John Doe")],
            album=album,
            genre="Technology",
            date="2014-06-15",
            length=424000,
            track_no=3,
        ),
        models.Track(
            uri="podcast+http://www.example.com/everything.xml#episode2",
            name="Socket Wrench Shootout",
            artists=[models.Artist(name="Jane Doe")],
            album=album,
            genre="Technology",
            date="2014-06-08",
            length=274000,
            track_no=2,
        ),
        models.Track(
            uri=(
                "podcast+http://www.example.com/everything.xml"
                "#http://example.com/everything/Episode1.mp3"
            ),
            name="Red, Whine, & Blue",
            artists=[models.Artist(name="Various")],
            album=album,
            genre="Technology",
            date="2014-06-01",
            length=239000,
            track_no=1,
        ),
    ]


@pytest.fixture
def items(tracks):
    return [models.Ref.track(uri=t.uri, name=t.name) for t in tracks]


def test_items(rss, items):
    assert list(rss.items(newest_first=True)) == items
    assert list(rss.items(newest_first=False)) == list(reversed(items))


def test_tracks(rss, tracks):
    assert list(rss.tracks(newest_first=True)) == tracks
    assert list(rss.tracks(newest_first=False)) == list(reversed(tracks))


def test_images(rss):
    assert dict(rss.images()) == {
        "podcast+http://www.example.com/everything.xml": [
            models.Image(uri="http://example.com/everything/Podcast.jpg")
        ],
        "podcast+http://www.example.com/everything.xml#episode3": [
            models.Image(uri="http://example.com/everything/Episode3.jpg")
        ],
        "podcast+http://www.example.com/everything.xml#episode2": [
            models.Image(uri="http://example.com/everything/Episode2.jpg")
        ],
        (
            "podcast+http://www.example.com/everything.xml"
            "#http://example.com/everything/Episode1.mp3"
        ): [models.Image(uri="http://example.com/everything/Podcast.jpg")],
    }
