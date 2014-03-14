from __future__ import unicode_literals
import unittest

from mopidy_podcast.backend import PodcastBackend


class BackendTest(unittest.TestCase):
    config = {
        'podcast': {
            'directories': [],
            'browse_label': None,
            'sort_order': 'asc',
            'update_interval': 86400,
            'cache_size': None,
            'cache_ttl': None,
            'timeout': None
        }
    }

    def setUp(self):
        self.backend = PodcastBackend(config=self.config, audio=None)
