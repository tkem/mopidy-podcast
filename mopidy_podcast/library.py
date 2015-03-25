from __future__ import unicode_literals

import logging
import operator
import uritools

from mopidy import backend
from mopidy.models import Album, Artist, Track, SearchResult

from . import Extension
from .models import Ref
from .query import Query

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


class PodcastLibraryProvider(backend.LibraryProvider):

    root_directory = Ref.directory(uri='podcast:', name='Podcasts')

    def __init__(self, config, backend):
        super(PodcastLibraryProvider, self).__init__(backend)
        self._config = config[Extension.ext_name]
        self._lookup = {}

    def lookup(self, uri):
        try:
            return [self._lookup[uri]]
        except KeyError:
            logger.debug('Podcast lookup cache miss: %s', uri)
        try:
            base, fragment = uritools.uridefrag(uri)
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

    def search(self, query=None, uris=None, exact=False):
        if exact:
            return self.find_exact(query, uris)
        if not query:
            return None
        try:
            q = Query(query, exact=False)
            return self._search(q, uris, self._config['search_limit'])
        except Exception as e:
            logger.error('Searching podcasts failed: %s', e)
            return None

    def _browse(self, uri, limit=None):
        refs = []
        for ref in self.backend.directory.browse(uri, limit):
            if ref.type == Ref.PODCAST:
                refs.append(Ref.album(uri=ref.uri, name=ref.name))
            elif ref.type == Ref.EPISODE:
                refs.append(Ref.track(uri=ref.uri, name=ref.name))
            else:
                refs.append(ref)
        return refs

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
