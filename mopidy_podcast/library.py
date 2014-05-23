from __future__ import unicode_literals

import logging
import operator

from mopidy import backend
from mopidy.models import Album, Artist, Track, SearchResult

from . import Extension
from .models import Ref
from .query import Query
from .timers import debug_timer
from .uritools import uridefrag

_QUERY_MAPPING = {
    'album': ('title', Ref.PODCAST),
    'albumartist': ('author', Ref.PODCAST),
    'artist': ('author', Ref.EPISODE),
    'comment': ('subtitle', Ref.EPISODE),
    'date': ('pubdate', None),
    'genre': ('category', Ref.PODCAST),
    'track_name': ('title', Ref.EPISODE),
    'any': (None, None)
}

logger = logging.getLogger(__name__)


def _wrap(ref, type=None):
    # TODO: translating no longer necessary with mopidy v0.19?
    name = ref.name.replace('"', "'").replace('/', '_')
    return ref.copy(name=name, type=type or ref.type)


class PodcastLibraryProvider(backend.LibraryProvider):

    def __init__(self, config, backend):
        super(PodcastLibraryProvider, self).__init__(backend)
        self._config = config[Extension.ext_name]
        self._lookup = {}
        # root directory for browsing
        self.root_directory = Ref.directory(
            uri=backend.directory.root_uri,
            name=self._config['root_name']
        )

    def lookup(self, uri):
        try:
            return [self._lookup[uri]]
        except KeyError:
            logger.debug('Podcast lookup cache miss: %s', uri)
        try:
            base, fragment = uridefrag(uri)
            if fragment:
                self._lookup = {t.uri: t for t in self._tracks(base)}
                return [self._lookup[uri]]
            else:
                tracks = self._tracks(base, self._config['browse_limit'])
                self._lookup = {t.uri: t for t in tracks}
                return tracks
        except Exception as e:
            logger.error('Podcast lookup failed for %s: %s', uri, e)
            return []

    def browse(self, uri):
        try:
            if not uri:
                return [self.root_directory]
            elif uri == self.root_directory.uri:
                return self.backend.directory.root_directories
            else:
                return self._browse(uri, self._config['browse_limit'])
        except Exception as e:
            logger.error('Browsing podcasts failed for %s: %s', uri, e)
            return None

    def find_exact(self, query=None, uris=None):
        if not query:
            return None
        try:
            q = Query(query, exact=True)
            return self._search(q, uris, self._config['search_limit'])
        except Exception as e:
            logger.error('Finding podcasts failed: %s', e)
            return None

    def search(self, query=None, uris=None):
        if not query:
            return None
        try:
            q = Query(query, exact=False)
            return self._search(q, uris, self._config['search_limit'])
        except Exception as e:
            logger.error('Searching podcasts failed: %s', e)
            return None

    @debug_timer(logger, 'Browsing podcasts')
    def _browse(self, uri, limit=None):
        refs = []
        for ref in self.backend.directory.browse(uri, limit):
            if ref.type == Ref.DIRECTORY:
                refs.append(_wrap(ref))
            elif ref.type == Ref.PODCAST:
                refs.append(_wrap(ref, Ref.DIRECTORY))
            elif ref.type == Ref.EPISODE:
                refs.append(_wrap(ref, Ref.TRACK))
            else:
                logger.warn('Invalid podcast browse result: %r', ref)
        return refs

    @debug_timer(logger, 'Searching podcasts')
    def _search(self, query, uris=None, limit=None):
        # only single search attribute supported
        if len(query) != 1 or query.keys()[0] not in _QUERY_MAPPING:
            return None
        attr, type = _QUERY_MAPPING[query.keys()[0]]
        terms = [v for values in query.values() for v in values]
        logger.debug('Searching %s.%s for %r in %r', type, attr, terms, uris)

        # merge results for multiple search uris
        results = []
        directory = self.backend.directory
        for uri in (uris or [directory.root_uri]):
            nleft = limit - len(results) if limit else None
            results.extend(directory.search(uri, terms, attr, type, nleft))
        # convert refs to albums and tracks
        if query.exact or self._config['search_details']:
            albums, tracks = self._load_search_results(results)
        else:
            albums, tracks = self._search_results(results)
        # filter results for exact queries
        if query.exact:
            albums = filter(query.match_album, albums)
            tracks = filter(query.match_track, tracks)
        return SearchResult(albums=albums, tracks=tracks)

    @debug_timer(logger, 'Loading search results')
    def _load_search_results(self, refs):
        directory = self.backend.directory
        albums = []
        tracks = []
        # sort by uri to improve lookup cache performance
        for ref in sorted(refs, key=operator.attrgetter('uri')):
            try:
                if ref.type == Ref.PODCAST:
                    albums.append(self._album(directory.get(ref.uri)))
                elif ref.type == Ref.EPISODE:
                    tracks.extend(self.lookup(ref.uri))
                else:
                    logger.warn('Invalid podcast search result: %r', ref)
            except Exception as e:
                logger.warn('Skipping search result %s: %s', ref.uri, e)
        return (albums, tracks)

    @debug_timer(logger, 'Converting search results')
    def _search_results(self, refs):
        albums = []
        tracks = []
        for ref in refs:
            if ref.type == Ref.PODCAST:
                albums.append(Album(uri=ref.uri, name=ref.name))
            elif ref.type == Ref.EPISODE:
                tracks.append(Track(uri=ref.uri, name=ref.name))
            else:
                logger.warn('Invalid podcast search result: %r', ref)
        return (albums, tracks)

    @debug_timer(logger, 'Getting tracks for podcast')
    def _tracks(self, uri, limit=None):
        podcast = self.backend.directory.get(uri)
        album = self._album(podcast)
        tracks = []
        for index, episode in enumerate(podcast.episodes[:limit], start=1):
            kwargs = {
                'uri': episode.uri,
                'name': episode.title,
                'artists': album.artists,  # default
                'album': album,
                'genre': podcast.category,
                'comment': episode.subtitle,
                'track_no': index
            }
            if episode.author:
                kwargs['artists'] = [Artist(name=episode.author)]
            if episode.pubdate:
                kwargs['date'] = episode.pubdate.date().isoformat()
            if episode.duration:
                kwargs['length'] = int(episode.duration.total_seconds() * 1000)
            if episode.subtitle:
                kwargs['comment'] = episode.subtitle
            tracks.append(Track(**kwargs))
        return tracks

    def _album(self, podcast):
        kwargs = {
            'uri': podcast.uri,
            'name': podcast.title,
            'num_tracks': len(podcast.episodes)
        }
        if podcast.author:
            kwargs['artists'] = [Artist(name=podcast.author)]
        if podcast.pubdate:
            kwargs['date'] = podcast.pubdate.date().isoformat()
        if podcast.image and podcast.image.uri:
            kwargs['images'] = [podcast.image.uri]
        return Album(**kwargs)
