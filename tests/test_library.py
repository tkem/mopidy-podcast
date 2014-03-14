from __future__ import unicode_literals

import unittest
import pykka

from mopidy_podcast.backend import PodcastBackend
from mopidy import core


class LibraryTest(unittest.TestCase):
    config = {
        'podcast': {
            'directories': [],
            'browse_label': None,
            'search_limit': None,
            'sort_order': 'desc',
            'update_interval': 86400,
            'cache_size': None,
            'cache_ttl': None,
            'timeout': None
        }
    }

    def setUp(self):
        PodcastBackend.registry = {'podcast:directory': []}
        self.backend = PodcastBackend.start(
            config=self.config, audio=None).proxy()
        self.core = core.Core(backends=[self.backend])
        self.library = self.core.library

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_search_artist(self):
        self.library.search(artist=['foo'])
        # TODO: write tests

    def test_search_album(self):
        self.library.search(album=['foo'])
        # TODO: write tests

    def test_search_date(self):
        self.library.search(date=['2014-02-01'])
        # TODO: write tests
