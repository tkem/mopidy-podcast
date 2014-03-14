from __future__ import unicode_literals

import datetime
import logging
import re

from mopidy import backend
from mopidy.models import Album, Artist, Track, SearchResult

from . import PodcastDirectory
from .models import Ref
from .query import Query
from .uritools import uridefrag

REFNAME_RE = re.compile(r'[/"]')

QUERY_MAP = {
    'any': None,
    'track_name': PodcastDirectory.TITLE,
    'album': PodcastDirectory.TITLE,
    'artist': PodcastDirectory.AUTHOR,
    'albumartist': PodcastDirectory.AUTHOR,
    'genre': PodcastDirectory.CATEGORY,
    'comment': PodcastDirectory.DESCRIPTION
}

logger = logging.getLogger(__name__)


def _keyfunc(e):
    return e.pubdate if e.pubdate else datetime.datetime.min


class PodcastLibraryProvider(backend.LibraryProvider):

    def __init__(self, backend):
        super(PodcastLibraryProvider, self).__init__(backend)
        self.root_directory = Ref.directory(
            uri='podcast:',
            name=self.config['browse_label']
        )
        # cache tracks for lookup
        self.tracks = {}

    @property
    def config(self):
        return self.backend.config[self.backend.name]

    def lookup(self, uri):
        try:
            return [self.tracks[uri]]
        except KeyError:
            logger.debug("Podcast lookup cache miss: %s", uri)
        try:
            defrag = uridefrag(uri)
            tracks = self._tracks(defrag.base)
            self.tracks = {track.uri: track for track in tracks}
            return [self.tracks[uri]] if defrag.fragment else tracks
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
                return self._browse(uri)
        except Exception as e:
            logger.error('Browsing podcasts failed for %s: %r', uri, e)
            return []

    def find_exact(self, query=None, uris=None):
        try:
            return self._search(Query(query, exact=True) if query else None)
        except Exception as e:
            logger.error('Searching podcasts failed: %r', e)

    def search(self, query=None, uris=None):
        try:
            return self._search(Query(query, exact=False) if query else None)
        except Exception as e:
            logger.error('Searching podcasts failed: %r', e)

    def _browse(self, uri):
        refs = []
        for ref in self.backend.directory.browse(uri):
            if ref.type == Ref.PODCAST:
                ref = ref.copy(type=Ref.DIRECTORY)
            elif ref.type == Ref.EPISODE:
                ref = ref.copy(type=Ref.TRACK)
            elif ref.type != Ref.DIRECTORY:
                logger.warn('Unexpected browse result for %s: %r', uri, ref)
            # FIXME: replace '/', '"' in names for browsing - really necessary?
            refs.append(ref.copy(name=REFNAME_RE.sub('_', ref.name or '')))
        return refs

    def _search(self, query=None):
        if query:
            if any(key not in QUERY_MAP for key in query.keys()):
                return None
            attribute = QUERY_MAP[query.keys()[0]]  # single attribute
            terms = [v for values in query.values() for v in values]
        else:
            attribute = terms = None
        limit = self.config['search_limit']

        albums = []
        tracks = []
        for ref in self.backend.directory.search(terms, attribute, limit):
            if ref.type == Ref.PODCAST:
                # minimum album info for performance reasons
                albums.append(Album(uri=ref.uri, name=ref.name))
            elif ref.type == Ref.EPISODE:
                tracks.extend(self.lookup(ref.uri))
            else:
                logger.warn('Unexpected podcast search result: %r', ref)
        # filter results for exact queries
        if query and query.exact:
            albums = [album for album in albums if query.match_album(album)]
            tracks = [track for track in tracks if query.match_track(track)]
        return SearchResult(albums=albums, tracks=tracks)

    def _album(self, podcast, uri):
        kwargs = {
            'uri': uri,
            'name': podcast.title,
            'num_tracks': len(podcast.episodes)
        }
        if podcast.author:
            kwargs['artists'] = [Artist(name=podcast.author)]
        if podcast.pubdate:
            kwargs['date'] = podcast.pubdate.date().isoformat()
        if podcast.image:
            kwargs['images'] = [podcast.image.url]
        return Album(**kwargs)

    def _tracks(self, uri):
        podcast = self.backend.directory.get(uri)
        album = self._album(podcast, uri)

        tracks = []
        for index, e in enumerate(self._sort_episodes(podcast.episodes)):
            if not e.enclosure or not e.enclosure.url:
                continue
            kwargs = {
                'uri': uri + '#' + e.enclosure.url,
                'name': e.title,
                'album': album,
                'artists': album.artists,
                'genre': podcast.category,
                'track_no': index + 1,
                'comment': e.subtitle  # or e.description?
            }
            if e.author:
                kwargs['artists'] = [Artist(name=e.author)]
            if e.pubdate:
                kwargs['date'] = e.pubdate.date().isoformat()
            if e.duration:
                kwargs['length'] = int(e.duration.total_seconds() * 1000)
            tracks.append(Track(**kwargs))
        return tracks

    def _sort_episodes(self, episodes):
        reverse = self.config['sort_order'] == 'desc'
        return sorted(episodes, key=_keyfunc, reverse=reverse)
