from __future__ import unicode_literals

import logging
import time

import feedparser

from mopidy import backend
from mopidy.models import SearchResult, Ref

from .translators import feed_to_ref, item_to_ref, item_to_track
from .uritools import uricompose, urisplit

logger = logging.getLogger(__name__)


class PodcastLibraryProvider(backend.LibraryProvider):

    def __init__(self, backend):
        super(PodcastLibraryProvider, self).__init__(backend)
        self.feeds = {url: None for url in self.getconfig('feed_urls')}
        self.root_directory = Ref.directory(
            uri='%s:/' % self.backend.URI_SCHEME,
            name=self.getconfig('browse_label'))
        if self.getconfig('preload'):
            for url in self.feeds:
                self.feeds[url] = self.getfeed(url)

    def browse(self, uri):
        logger.debug("podcast browse: %s", uri)

        if not uri:
            return [self.root_directory]
        elif uri == self.root_directory.uri:
            return self._browse_root()
        else:
            return self._browse_feed(urisplit(uri).getauthority())

    def lookup(self, uri):
        #logger.debug("podcast lookup: %s", uri)

        uriparts = urisplit(uri)
        feeduri = uriparts.getauthority()
        feed = self.getfeed(feeduri)
        guid = uriparts.getpath().lstrip('/')
        # FIXME: temporary workaround for MPoD timeout
        if 'tracks' not in feed:
            logger.debug("podcast %s: building track cache", feeduri)
            feed['tracks'] = {}
            for index, item in enumerate(reversed(feed.entries)):
                feed['tracks'][item.guid] = item_to_track(feed, item, index)
        if guid in feed['tracks']:
            return [feed['tracks'][guid]]
        logger.debug("podcast lookup failed: %s [%s]", feeduri, guid)
        return []

    def search(self, query=None, uris=None):
        logger.debug("podcast search: %r", query)
        return None

    def getconfig(self, name):
        return self.backend.getconfig(name)

    def getfeed(self, url, update=False):
        #logger.debug("getting podcast %s", url)
        feed = self.feeds[url]

        # FIXME: etag/modified not working as expected?
        if not feed:
            logger.debug("loading podcast %s", url)
            feed = self.feeds[url] = feedparser.parse(url)
            feed['downloaded'] = time.time()
        elif update and feed['downloaded'] < time.time() - 3600:
            logger.debug("updating podcast %s", url)
            if feed.etag:
                logger.debug("podcast %s: checking etag", url)
                newfeed = feedparser.parse(url, etag=feed.etag)
            elif feed.modified:
                logger.debug("podcast %s: checking modified", url)
                newfeed = feedparser.parse(url, modified=feed.modified)
            else:
                newfeed = feedparser.parse(url)

            if newfeed.feed:
                logger.debug("updated podcast %s", url)
                feed = newfeed
                feed['downloaded'] = time.time()
            else:
                logger.debug("unchanged podcast %s", url)
        return feed

    def _browse_root(self):
        refs = []
        for url in self.feeds:
            feed = self.getfeed(url)
            refs.append(feed_to_ref(feed, Ref.DIRECTORY))
        return refs

    def _browse_feed(self, url):
        logger.debug("podcast browse feed: %s", url)
        feed = self.getfeed(url, True)

        refs = []
        for item in feed.entries:
            refs.append(item_to_ref(feed, item))
        return refs
