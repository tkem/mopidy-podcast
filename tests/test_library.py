from __future__ import unicode_literals

import unittest
import pykka

from mopidy_podcast.backend import PodcastBackend
from mopidy import core


class LibraryTest(unittest.TestCase):
    config = {
        'podcast': {
            'root_name': '',
            'browse_limit': None,
            'search_limit': None,
            'update_interval': 86400
        }
    }

    def setUp(self):
        self.backend = PodcastBackend.start(self.config, None).proxy()
        self.library = core.Core(backends=[self.backend]).library

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
