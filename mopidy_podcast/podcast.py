from __future__ import unicode_literals

import logging
import time

import feedparser

from mopidy.models import Album, Artist, Track, Ref

from .uritools import uricompose

logger = logging.getLogger(__name__)


def _parse_duration(s):
    if not s:
        return None
    hms = (list(reversed(s.split(':', 2))) + [0, 0])[0:3]
    return int((float(hms[0]) + int(hms[1]) * 60 + int(hms[2]) * 3600) * 1000)


class Podcast(object):

    URI_SCHEME = 'podcast'

    def __init__(self, feed_url):
        self.feed_url = feed_url
        self.update()


    def update(self):
        # TODO: check etag, modified...
        fd = feedparser.parse(self.feed_url)

        album = Album(
            uri=uricompose(self.URI_SCHEME, path=self.feed_url),
            name=fd.feed.title,
            artists=[Artist(name=fd.feed.author)],
            num_tracks=len(fd.entries),
            date=time.strftime('%Y-%m-%d', fd.feed.updated_parsed),
            images=[fd.feed.image.href] if 'image' in fd.feed else []
        )

        refs = []
        tracks = {}
        # TODO: sort by pubDate, ...?
        for index, item in enumerate(fd.entries):
            # FIXME: assuming guid == link to mp3
            uri=uricompose(
                self.URI_SCHEME,
                path=self.feed_url,
                fragment=item.guid
            )
            tracks[item.guid] = Track(
                uri=uri,
                name=item.title,
                artists=[Artist(name=item.get('author', fd.feed.author))],
                album=album,
                track_no=index + 1,
                date=time.strftime('%Y-%m-%d', item.published_parsed),
                length=_parse_duration(item.get('itunes_duration'))
            )
            refs.append(Ref.track(uri=uri, name=item.title))

        self.album = album
        self.tracks = tracks
        self.refs = refs
        self.updated = time.time()
