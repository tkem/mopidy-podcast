from __future__ import unicode_literals

import logging

from mopidy import backend
#from mopidy.models import SearchResult, Ref

#from .translators import item_to_tracks, file_to_ref, doc_to_ref, doc_to_album
#from .uritools import uricompose, urisplit

logger = logging.getLogger(__name__)


class PocastLibraryProvider(backend.LibraryProvider):

    def __init__(self, backend):
        super(PodcastLibraryProvider, self).__init__(backend)

    def browse(self, uri):
        logger.debug("podcats browse: %s", uri)
        return []

    def lookup(self, uri):
        logger.debug("podcast lookup: %s", uri)
        return []

    def search(self, query=None, uris=None):
        logger.debug("podcast search: %r", query)
        return None

    def getconfig(self, name):
        return self.backend.getconfig(name)
