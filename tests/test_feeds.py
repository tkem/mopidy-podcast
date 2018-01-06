from __future__ import unicode_literals

import pytest

import uritools

from mopidy_podcast import feeds

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


@pytest.mark.parametrize('filename,expected', [
    ('directory.xml', feeds.OpmlFeed),
    ('rssfeed.xml', feeds.RssFeed),

])
def test_parse(abspath, filename, expected):
    path = abspath(filename)
    feed = feeds.parse(path)
    assert isinstance(feed, expected)
    assert feed.uri == uritools.uricompose('podcast+file', '', path)


def test_case_sensitive_parse():
    xml = r'''<?xml version="1.0" encoding="utf-8" ?>
    <opml version="1.1">
        <head title="Podcasts">
            <expansionState></expansionState>
        </head>
        <body>
            <outline URL="http://example.com/" text="example" type="link" />
        </body>
    </opml>
    '''
    root = ElementTree.fromstring(xml)
    feed = feeds.OpmlFeed('foo', root)
    assert feed.items().next().uri == 'podcast+http://example.com/'
