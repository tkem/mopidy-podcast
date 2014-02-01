from __future__ import unicode_literals

from time import strftime, strptime

from mopidy.models import Track, Album, Artist, Ref

from .uritools import uricompose

URI_SCHEME = 'podcast'


def feed_to_ref(feed, type=None):
    name = feed.feed.title if 'title' in feed.feed else 'unknown'
    uri = uricompose(URI_SCHEME, feed.href)

    if type is not None:
        return Ref(uri=uri, name=name, type=type)
    else:
        return Ref.album(uri=uri, name=name)

def item_to_ref(feed, item, type=None):
    name = item.title if 'title' in item else 'unknown'
    uri = uricompose(URI_SCHEME, feed.href, item.guid)

    if type is not None:
        return Ref(uri=uri, name=name, type=type)
    else:
        return Ref.track(uri=uri, name=name)

def feed_to_album(feed):
    return Album(
        uri=uricompose(URI_SCHEME, feed.href),
        name=feed.feed.title,
        artists=[Artist(name=feed.feed.author)],
        date=strftime('%Y-%m-%d', feed.feed.updated_parsed)
    )

def item_to_track(feed, item, index):
    album = feed_to_album(feed)
    return Track(
        uri=uricompose(URI_SCHEME, feed.href, item.guid),
        name=item.title if 'title' in item else 'unknown',
        artists=album.artists,
        album=album,
        track_no=index + 1,
        date=strftime('%Y-%m-%d', item.published_parsed),
        length=parse_duration(item.get('itunes_duration'))
    )


def parse_duration(s):
    if not s:
        return None
    hms = (list(reversed(s.split(':', 2))) + [0, 0])[0:3]
    return int((float(hms[0]) + int(hms[1]) * 60 + int(hms[2]) * 3600) * 1000)
