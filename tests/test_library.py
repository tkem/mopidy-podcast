from __future__ import unicode_literals

import unittest
import pykka

from mopidy_podcast.backend import PodcastBackend
from mopidy import core


class LibraryTest(unittest.TestCase):
    config = {
        'podcast': {
            'feed_urls': [],
            'browse_label': 'Podcasts',
            'update_interval': 0,
            'sort_order': 'desc'
        }
    }

    def setUp(self):
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
