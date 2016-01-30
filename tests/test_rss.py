from __future__ import unicode_literals

import pytest

from mopidy_podcast import feeds


XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">
<channel>
<title>All About Everything</title>
<link>http://www.example.com/podcasts/everything/index.html</link>
<language>en-us</language>
<copyright>&#x2117; &amp; &#xA9; 2014 John Doe &amp; Family</copyright>
</channel>
</rss>"""


@pytest.fixture
def rss():
    from StringIO import StringIO

    class StringSource(StringIO):
        def geturl(self):
            return 'http://example.com/example.rss'

    return StringSource(XML)


def test_items(rss):
    assert list(feeds.parse(rss).items()) == []


def test_tracks(rss):
    assert list(feeds.parse(rss).tracks()) == []


def test_images(rss):
    assert dict(feeds.parse(rss).images()) == {}
