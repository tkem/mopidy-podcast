from __future__ import unicode_literals

import collections
import logging

logger = logging.getLogger(__name__)

QUERY_FIELDS = {
    'uri',
    'track_name',
    'track_no',
    'album',
    'artist',
    'composer',
    'performer',
    'albumartist',
    'genre',
    'date',
    'comment',
    'any'
}

DEFAULT_FILTERS = dict.fromkeys(QUERY_FIELDS, lambda qv, value: False)

TRACK_FILTERS = dict(
    DEFAULT_FILTERS,
    uri=lambda qv, track: qv == track.uri,
    track_name=lambda qv, track: qv == track.name,
    track_no=lambda qv, track: str(qv).isdigit() and int(qv) == track.track_no,
    album=lambda qv, track: track.album and qv == track.album.name,
    artist=lambda qv, track: any(
        qv == a.name for a in track.artists
    ),
    composer=lambda qv, track: any(
        qv == a.name for a in track.composers
    ),
    performer=lambda qv, track: any(
        qv == a.name for a in track.performers
    ),
    albumartist=lambda qv, track: track.album and any(
        qv == a.name for a in track.album.artists
    ),
    genre=lambda qv, track: qv == track.genre,
    date=lambda qv, track: qv == track.date,
    comment=lambda qv, track: qv == track.comment
)

ALBUM_FILTERS = dict(
    DEFAULT_FILTERS,
    uri=lambda qv, album: qv == album.uri,
    album=lambda qv, album: qv == album.name,
    artist=lambda qv, album: any(
        qv == a.name for a in album.artists
    ),
    albumartist=lambda qv, album: any(
        qv == a.name for a in album.artists
    ),
    date=lambda qv, album: qv == album.date
)

ARTIST_FILTERS = dict(
    DEFAULT_FILTERS,
    uri=lambda qv, artist: qv == artist.uri,
    artist=lambda qv, artist: qv == artist.name
)


# setup 'any' filters
def _any_filter(filtermap):
    filters = [filtermap[key] for key in filtermap.keys() if key != 'any']

    def any_filter(qv, value):
        return any(f(qv, value) for f in filters)
    return any_filter

TRACK_FILTERS['any'] = _any_filter(TRACK_FILTERS)
ALBUM_FILTERS['any'] = _any_filter(ALBUM_FILTERS)
ARTIST_FILTERS['any'] = _any_filter(ARTIST_FILTERS)


class Query(collections.Mapping):

    class QV(object):

        def __init__(self, value):
            self.__value = value.strip().lower()

        def __eq__(self, other):
            return other and self.__value in other.lower()

        def __ne__(self, other):
            return not other or self.__value not in other.lower()

        def __str__(self):
            return self.__value

        def __int__(self):
            return int(self.__value)

        __hash__ = None

    def __init__(self, query, exact=False):
        self.__query = {}
        for field, values in query.iteritems():
            if field not in QUERY_FIELDS:
                raise LookupError('Invalid query field "%s"' % field)
            if not values:
                raise LookupError('Missing query value for "%s"' % field)
            if not hasattr(values, '__iter__'):
                values = [values]
            if not all(values):
                raise LookupError('Missing query value for "%s"' % field)
            if exact:
                self.__query[field] = values
            else:
                self.__query[field] = [self.QV(value) for value in values]

    def __getitem__(self, key):
        return self.__query.__getitem__(key)

    def __iter__(self):
        return self.__query.__iter__()

    def __len__(self):
        return self.__query.__len__()

    def filter_tracks(self, tracks):
        return filter(self._get_filter(TRACK_FILTERS), tracks)

    def filter_albums(self, albums):
        return filter(self._get_filter(ALBUM_FILTERS), albums)

    def filter_artists(self, artists):
        return filter(self._get_filter(ARTIST_FILTERS), artists)

    def _get_filter(self, filtermap):
        from functools import partial
        filters = []
        for field, values in self.__query.iteritems():
            filters.extend(partial(filtermap[field], qv) for qv in values)

        def filterfunc(model):
            return all(f(model) for f in filters)
        return filterfunc
