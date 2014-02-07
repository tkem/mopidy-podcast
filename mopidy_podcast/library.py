from __future__ import unicode_literals

import itertools
import logging
import time

from mopidy import backend
from mopidy.models import Album, Artist, Track, Ref, SearchResult

from .podcast import Podcast
from .query import Query
from .uritools import uricompose, urisplit

logger = logging.getLogger(__name__)


class DebugTimer(object):
    def __init__(self, msg):
        self.msg = msg
        self.start = None

    def __enter__(self):
        logger.debug('%s...', self.msg)
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        duration = (time.time() - self.start) * 1000
        logger.debug('%s took %dms', self.msg, duration)


class PodcastLibraryProvider(backend.LibraryProvider):

    PODCAST, ALBUM, TRACKS, TIMESTAMP = (0, 1, 2, 3)

    def __init__(self, backend):
        super(PodcastLibraryProvider, self).__init__(backend)
        self.uri_scheme = self.backend.URI_SCHEME
        self.root_directory = Ref.directory(
            uri=uricompose(self.uri_scheme, path='/'),
            name=self.getconfig('browse_label')
        )

        self.podcasts = {}
        for url in self.getconfig('feed_urls'):
            try:
                self.podcasts[url] = self._load_podcast(url)
            except Exception as e:
                logger.error('Error loading podcast %s: %s', url, e)
                raise
        logger.info("Loaded %d podcasts", len(self.podcasts))

    def browse(self, uri):
        logger.debug("browse podcasts %s", uri)

        if not uri:
            return [self.root_directory]
        elif uri == self.root_directory.uri:
            return self._browse_root()
        else:
            return self._browse_podcast(urisplit(uri).getpath())

    def lookup(self, uri):
        logger.debug("lookup podcast %s", uri)
        uriparts = urisplit(uri)
        podcast = self.podcasts.get(uriparts.getpath())

        if not podcast:
            return []
        elif not uriparts.fragment:
            return podcast[self.TRACKS].values()
        else:
            return [podcast[self.TRACKS][uriparts.getfragment()]]

    def search(self, query=None, uris=None):
        logger.debug("search podcasts %r", query)
        query = Query(query, False)
        tracks = [p[self.TRACKS].values() for p in self.podcasts.values()]
        albums = [p[self.ALBUM] for p in self.podcasts.values()]

        return SearchResult(
            uri=uricompose(self.uri_scheme, query=str(query)),
            tracks=query.filter_tracks(itertools.chain(*tracks)),
            albums=query.filter_albums(albums)
        )

    def getstream(self, uri):
        # FIXME: fragment == stream url ???
        return urisplit(uri).getfragment()

    def getconfig(self, name):
        return self.backend.getconfig(name)

    def _load_podcast(self, url):
        with DebugTimer('Loading podcast %s' % url):
            podcast = Podcast(url)
        album = self._podcast_to_album(podcast)
        tracks = {}
        for index, e in enumerate(self._sort_episodes(podcast)):
            kwargs = {
                'uri': uricompose(self.uri_scheme, path=url, fragment=e.guid),
                'name': e.title,
                'album': album,
                'genre': podcast.category,
                'track_no': index + 1,
                'comment': e.subtitle
            }
            if e.author:
                kwargs['artists'] = [Artist(name=e.author)]
            else:
                kwargs['artists'] = album.artists
            if e.pubdate:
                kwargs['date'] = e.pubdate.date().isoformat()
            if e.duration:
                kwargs['length'] = int(e.duration.total_seconds() * 1000)
            tracks[e.guid] = Track(**kwargs)
        return (podcast, album, tracks, time.time())

    def _browse_root(self):
        refs = []
        for podcast in self.podcasts.values():
            ref = Ref.directory(
                uri=podcast[self.ALBUM].uri,
                name=podcast[self.ALBUM].name
            )
            refs.append(ref)
        return refs

    def _browse_podcast(self, url):
        podcast = self.podcasts[url]
        refs = []
        for track in podcast[self.TRACKS].values():
            ref = Ref.track(
                uri=track.uri,
                name=track.name
            )
            refs.append(ref)
        return refs

    def _podcast_to_album(self, podcast):
        kwargs = {
            'uri': uricompose(self.uri_scheme, path=podcast.url),
            'name': podcast.title,
            'num_tracks': len(podcast)
        }
        if podcast.author:
            kwargs['artists'] = [Artist(name=podcast.author)]
        if podcast.image and 'href' in podcast.image:
            kwargs['images'] = [podcast.image['href']]
        # TBD: date
        return Album(**kwargs)

    def _sort_episodes(self, podcast):
        reverse = self.getconfig('sort_order') == 'desc'

        def keyfunc(e):
            from datetime import datetime
            return e.pubdate if e.pubdate else datetime.min

        return sorted(podcast.episodes, key=keyfunc, reverse=reverse)
