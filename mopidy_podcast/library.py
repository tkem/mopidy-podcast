from __future__ import unicode_literals

import logging
import time

from mopidy import backend
from mopidy.models import SearchResult, Ref

from .podcast import Podcast
from .uritools import urisplit

logger = logging.getLogger(__name__)


class PodcastLibraryProvider(backend.LibraryProvider):

    def __init__(self, backend):
        super(PodcastLibraryProvider, self).__init__(backend)
        self.root_directory = Ref.directory(
            uri='%s:/' % self.backend.URI_SCHEME,
            name=self.getconfig('browse_label'))
        self.podcasts = {url: None for url in self.getconfig('feed_urls')}

        if self.getconfig('preload'):
            for url in self.podcasts:
                self.podcasts[url] = self.getpodcast(url)

    def browse(self, uri):
        logger.debug("browse podcasts: %s", uri)

        if not uri:
            return [self.root_directory]
        elif uri == self.root_directory.uri:
            return self._browse_root()
        else:
            return self._browse_podcast(urisplit(uri).getpath())

    def lookup(self, uri):
        logger.debug("lookup podcast: %s", uri)

        uriparts = urisplit(uri)
        podcast = self.getpodcast(uriparts.getpath())
        if not podcast:

            return []
        if not uriparts.fragment:
            return podcast.tracks.values()
        return [podcast.tracks[uriparts.getfragment()]]

    def search(self, query=None, uris=None):
        logger.debug("podcast search: %r", query)
        return None

    def getconfig(self, name):
        return self.backend.getconfig(name)

    def getpodcast(self, url, update=False):
        logger.debug('loading podcast %s', url)
        if not self.podcasts.get(url):
            try:
                self.podcasts[url] = Podcast(url)
            except Exception as e:
                logger.error('Error loading podcast %s: %s', url, e)
                return None

        podcast = self.podcasts[url]
        if update and podcast.updated < time.time() - 3600:
            try:
                podcast.update()
            except Exception as e:
                logger.error('Error loading podcast %s: %s', url, e)
        return podcast

    def _browse_root(self):
        refs = []
        for url in self.podcasts:
            podcast = self.getpodcast(url)
            if podcast:
                refs.append(Ref.directory(
                    uri=podcast.album.uri,
                    name=podcast.album.name))
        return refs

    def _browse_podcast(self, url):
        podcast = self.getpodcast(url, True)
        if podcast:
            return podcast.refs
        else:
            return []
