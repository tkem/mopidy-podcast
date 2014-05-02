from __future__ import unicode_literals

import logging
import operator

from mopidy import backend
from mopidy.models import Album, Artist, Track, SearchResult

from .directory import PodcastDirectory
from .models import Ref
from .query import Query
from .timers import debug_timer
from .uritools import uridefrag, urisplit, uriencode

_QUERY_MAPPING = {
    'album': (PodcastDirectory.TITLE, Ref.PODCAST),
    'albumartist': (PodcastDirectory.AUTHOR, Ref.PODCAST),
    'artist': (PodcastDirectory.AUTHOR, Ref.EPISODE),
    'comment': (PodcastDirectory.DESCRIPTION, None),
    'genre': (PodcastDirectory.CATEGORY, None),  # FIXME: PODCAST?
    'track_name': (PodcastDirectory.TITLE, Ref.EPISODE),
    'any': (None, None)
}

logger = logging.getLogger(__name__)


def _wrap(ref, type=None):
    # TODO: new uri scheme:
    # - podcast://dirname/...
    # - podcast+http://...
    # - podcast+https://...
    # blocked by https://github.com/mopidy/mopidy/issues/708
    defrag = uridefrag(ref.uri)
    #logger.info('WRAP: %r', defrag)
    if defrag.fragment:
        uri = 'podcast:' + uriencode(defrag.base) + '#' + defrag.fragment
    else:
        uri = 'podcast:' + uriencode(defrag.base)
    # FIXME: translating probably no longer necessary with mopidy v0.19
    name = unicode(ref.name).translate({ord('"'): "'", ord('/'): '_'})
    return ref.copy(uri=uri, name=name, type=type or ref.type)


class PodcastLibraryProvider(backend.LibraryProvider):

    def __init__(self, backend):
        super(PodcastLibraryProvider, self).__init__(backend)
        self._config = self.backend.config[self.backend.name]
        self._lookup = {}  # cache tracks for lookup
        self.root_directory = Ref.directory(
            uri='podcast:',
            name=self._config['browse_label']
        )

    def lookup(self, uri):
        try:
            return [self._lookup[uri]]
        except KeyError:
            logger.debug('Podcast lookup cache miss: %s', uri)
        try:
            feedurl, fragment = uridefrag(uri)
            if fragment:
                self._lookup = {t.uri: t for t in self._tracks(feedurl)}
                return [self._lookup[uri]]
            else:
                tracks = self._tracks(feedurl, self._config['browse_limit'])
                self._lookup = {t.uri: t for t in tracks}
                return tracks
        except Exception as e:
            logger.error('Podcast lookup failed for %s: %r', uri, e)
            return []

    def browse(self, uri):
        try:
            if not uri:
                return [self.root_directory]
            elif uri == self.root_directory.uri:
                return self._browse(None)
            else:
                return self._browse(uri, self._config['browse_limit'])
        except Exception as e:
            logger.error('Browsing podcasts failed for %s: %r', uri, e)
            raise  # FIXME: remove
            return []

    def find_exact(self, query=None, uris=None):
        try:
            q = Query(query, exact=True) if query else None
            return self._search(q, uris, self._config['search_limit'])
        except Exception as e:
            logger.error('Finding podcasts failed: %r', e)

    def search(self, query=None, uris=None):
        try:
            q = Query(query, exact=False) if query else None
            return self._search(q, uris, self._config['search_limit'])
        except Exception as e:
            logger.error('Searching podcasts failed: %r', e)

    @debug_timer(logger, 'Browsing podcasts')
    def _browse(self, uri, limit=None):
        path = urisplit(uri).getpath() if uri else None
        refs = []
        for ref in self.backend.directory.browse(path, limit):
            if ref.type == Ref.DIRECTORY or ref.type == Ref.PODCAST:
                refs.append(_wrap(ref, Ref.DIRECTORY))
            elif ref.type == Ref.EPISODE:
                refs.append(_wrap(ref, Ref.TRACK))
            else:
                logger.warn('Unexpected podcast browse result: %r', ref)
        return refs

    @debug_timer(logger, 'Searching podcasts')
    def _search(self, query=None, uris=None, limit=None):
        if query:
            if len(query) > 1 or query.keys()[0] not in _QUERY_MAPPING:
                return None
            terms = [v for values in query.values() for v in values]
            attr, type = _QUERY_MAPPING[query.keys()[0]]
        else:
            terms = attr = type = None
        directory = self.backend.directory

        albums = []
        tracks = []
        for uri in (uris or [None]):
            path = urisplit(uri).getpath() if uri else None
            # TODO: adapt limit for multiple uris
            refs = directory.search(terms, attr, type, path, limit)
            # sort by uri to improve lookup cache performance
            for ref in sorted(refs, key=operator.attrgetter('uri')):
                if ref.type == Ref.PODCAST:
                    # only minimum album info for performance reasons
                    albums.append(Album(uri=_wrap(ref).uri, name=ref.name))
                elif ref.type == Ref.EPISODE:
                    # lookup also preloads tracks into cache
                    tracks.extend(self.lookup(_wrap(ref).uri))
                else:
                    logger.warn('Unexpected podcast search result: %r', ref)
        # filter results for exact queries only
        if query and query.exact:
            albums = [album for album in albums if query.match_album(album)]
            tracks = [track for track in tracks if query.match_track(track)]
        return SearchResult(albums=albums, tracks=tracks)

    @debug_timer(logger, 'Getting tracks for podcast')
    def _tracks(self, uri, limit=None):
        podcast = self.backend.directory.get(urisplit(uri).getpath())
        if self._config['sort_order'] == 'desc':
            episodes = podcast.episodes[:limit]
            start = 1
        else:
            episodes = reversed(podcast.episodes[:limit])
            start = max(len(podcast.episodes) - limit, 1) if limit else 1
        album = self._album(podcast, uri)

        tracks = []
        for index, e in enumerate(episodes, start=start):
            if not e.uri:
                continue
            kwargs = {
                'uri': uri + '#' + e.enclosure.uri,  # TODO
                'name': e.title,
                'album': album,
                'artists': album.artists,
                'genre': podcast.category,
                'track_no': index
            }
            if e.author:
                kwargs['artists'] = [Artist(name=e.author)]
            if e.pubdate:
                kwargs['date'], _, _ = e.pubdate.partition('T')
            if e.duration:
                kwargs['length'] = e.duration
            tracks.append(Track(**kwargs))
        return tracks

    def _album(self, podcast, uri):
        kwargs = {
            'uri': uri,
            'name': podcast.title,
            'num_tracks': len(podcast.episodes)
        }
        if podcast.author:
            kwargs['artists'] = [Artist(name=podcast.author)]
        if podcast.pubdate:
            kwargs['date'], _, _ = podcast.pubdate.partition('T')
        if podcast.image and podcast.image.uri:
            kwargs['images'] = [podcast.image.uri]
        return Album(**kwargs)
