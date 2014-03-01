from __future__ import unicode_literals

import collections

from mopidy.models import Artist, Album, Track

QUERY_FIELDS = {
    'uri',
    'track_name',
    'album',
    'artist',
    'composer',
    'performer',
    'albumartist',
    'genre',
    'date',
    'comment',
    'track_no',
    'any'
}

DEFAULT_FILTERS = dict.fromkeys(QUERY_FIELDS, lambda q, v: False)

TRACK_FILTERS = [
    dict(
        DEFAULT_FILTERS,
        uri=lambda q, track: bool(
            track.uri and q in track.uri.lower()
        ),
        track_name=lambda q, track: bool(
            track.name and q in track.name.lower()
        ),
        album=lambda q, track: bool(
            track.album and track.album.name and q in track.album.name.lower()
        ),
        artist=lambda q, track: any(
            a.name and q in a.name.lower() for a in track.artists
        ),
        composer=lambda q, track: any(
            a.name and q in a.name.lower() for a in track.composers
        ),
        performer=lambda q, track: any(
            a.name and q in a.name.lower() for a in track.performers
        ),
        albumartist=lambda q, track: track.album and any(
            a.name and q in a.name.lower() for a in track.album.artists
        ),
        genre=lambda q, track: bool(
            track.genre and q in track.genre.lower()
        ),
        date=lambda q, track: bool(
            track.date and track.date.startswith(q)
        ),
        comment=lambda q, track: bool(
            track.comment and q in track.comment.lower(),
        ),
        track_no=lambda q, track: q.isdigit() and int(q) == track.track_no
    ),
    dict(
        DEFAULT_FILTERS,
        uri=lambda q, track: q == track.uri,
        track_name=lambda q, track: q == track.name,
        album=lambda q, track: track.album and q == track.album.name,
        artist=lambda q, track: any(
            q == a.name for a in track.artists
        ),
        composer=lambda q, track: any(
            q == a.name for a in track.composers
        ),
        performer=lambda q, track: any(
            q == a.name for a in track.performers
        ),
        albumartist=lambda q, track: track.album and any(
            q == a.name for a in track.album.artists
        ),
        genre=lambda q, track: q == track.genre,
        date=lambda q, track: q == track.date,
        comment=lambda q, track: q == track.comment,
        track_no=lambda q, track: q.isdigit() and int(q) == track.track_no
    )
]

ALBUM_FILTERS = [
    dict(
        DEFAULT_FILTERS,
        uri=lambda q, album: bool(album.uri and q in album.uri.lower()),
        album=lambda q, album: bool(album.name and q in album.name.lower()),
        artist=lambda q, album: any(
            a.name and q in a.name.lower() for a in album.artists
        ),
        albumartist=lambda q, album: any(
            a.name and q in a.name.lower() for a in album.artists
        ),
        date=lambda q, album: bool(
            album.date and album.date.startswith(q)
        )
    ),
    dict(
        DEFAULT_FILTERS,
        uri=lambda q, album: q == album.uri,
        album=lambda q, album: q == album.name,
        artist=lambda q, album: any(
            q == a.name for a in album.artists
        ),
        albumartist=lambda q, album: any(
            q == a.name for a in album.artists
        ),
        date=lambda q, album: q == album.date
    )
]

ARTIST_FILTERS = [
    dict(
        DEFAULT_FILTERS,
        uri=lambda q, artist: bool(artist.uri and q in artist.uri.lower()),
        artist=lambda q, artist: bool(artist.name and q in artist.name.lower())
    ),
    dict(
        DEFAULT_FILTERS,
        uri=lambda q, artist: q == artist.uri,
        artist=lambda q, artist: q == artist.name
    )
]


class Query(collections.Mapping):

    _track_filter = None
    _album_filter = None
    _artist_filter = None

    def __init__(self, terms, exact=False):
        if not terms:
            raise LookupError('Empty query not allowed')
        self.terms = {}
        self.exact = exact

        for field, values in terms.iteritems():
            if field not in QUERY_FIELDS:
                raise LookupError('Invalid query field %r' % field)
            if isinstance(values, basestring):
                values = [values]
            if not (values and all(values)):
                raise LookupError('Missing query value for %r' % field)
            if exact:
                self.terms[field] = values
            else:
                self.terms[field] = [v.lower() for v in values]

    def __getitem__(self, key):
        return self.terms[key]

    def __iter__(self):
        return iter(self.terms)

    def __len__(self):
        return len(self.terms)

    def match(self, model):
        if isinstance(model, Track):
            return self.match_track(model)
        elif isinstance(model, Album):
            return self.match_album(model)
        elif isinstance(model, Artist):
            return self.match_artist(model)
        else:
            raise TypeError('Invalid model type: %s' % type(model))

    def match_artist(self, artist):
        if not self._artist_filter:
            self._artist_filter = self._filter(ARTIST_FILTERS[self.exact])
        return self._artist_filter(artist)

    def match_album(self, album):
        if not self._album_filter:
            self._album_filter = self._filter(ALBUM_FILTERS[self.exact])
        return self._album_filter(album)

    def match_track(self, track):
        if not self._track_filter:
            self._track_filter = self._filter(TRACK_FILTERS[self.exact])
        return self._track_filter(track)

    def _filter(self, filtermap):
        from functools import partial
        filters = []
        for field, values in self.terms.iteritems():
            filters.extend(partial(filtermap[field], v) for v in values)

        def func(model):
            return all(f(model) for f in filters)
        return func


# setup 'any' filters
def _any_filter(filtermap):
    filters = filtermap.values()

    def any_filter(q, v):
        return any(f(q, v) for f in filters)
    return any_filter

for i in (False, True):
    TRACK_FILTERS[i]['any'] = _any_filter(TRACK_FILTERS[i])
    ALBUM_FILTERS[i]['any'] = _any_filter(ALBUM_FILTERS[i])
    ARTIST_FILTERS[i]['any'] = _any_filter(ARTIST_FILTERS[i])
