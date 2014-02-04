from __future__ import unicode_literals

import logging
import re
import time

import feedparser

from mopidy.models import Album, Artist, Track, Ref

from .uritools import uricompose

DURATION_RE = re.compile(r"""
(?:
    (?:(?P<hours>\d+):)?
    (?P<minutes>\d+):
)?
(?P<seconds>\d+(?:\.?\d+)?)
""", flags=(re.VERBOSE))

logger = logging.getLogger(__name__)


def _parse_date(t):
    return time.strftime('%Y-%m-%d', t) if t else None

def _parse_duration(s):
    from datetime import timedelta
    match = DURATION_RE.match(s or '')
    if not match:
        return None
    kwargs = {k: float(v) for k, v in match.groupdict('0').items()}
    return int(timedelta(**kwargs).total_seconds() * 1000)


class Podcast(object):

    URI_SCHEME = 'podcast'

    def __init__(self, feed_url):
        self.feed_url = feed_url
        self.update()


    def update(self):
        # TODO: check etag, modified...
        fd = feedparser.parse(self.feed_url)

        # FIXME: multiple authors
        artists=[Artist(name=fd.feed.author)]

        album = Album(
            uri=uricompose(self.URI_SCHEME, path=self.feed_url),
            name=fd.feed.title,
            artists=artists,
            num_tracks=len(fd.entries),
            date=_parse_date(fd.feed.get('updated_parsed')),
            images=[fd.feed.image.href] if 'image' in fd.feed else []
        )

        genre = fd.feed.get('category')

        refs = []
        tracks = {}
        # TODO: sort by pubDate asc/desc, itunes_order, ...
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
                genre=genre,
                track_no=index + 1,
                date=_parse_date(item.get('published_parsed')),
                length=_parse_duration(item.get('itunes_duration')),
                #comment=item.get('description')
            )
            refs.append(Ref.track(uri=uri, name=item.title))

        self.album = album
        self.tracks = tracks
        self.refs = refs
        self.updated = time.time()
