from __future__ import unicode_literals
import unittest

from mopidy_podcast.backend import PodcastBackend


class BackendTest(unittest.TestCase):
    config = {
        'podcast': {
            'feed_urls': ['http://www.npr.org/rss/podcast.php?id=510019'],
            'browse_label': 'Podcasts',
            'preload': False
        }
    }

    def setUp(self):
        self.backend = PodcastBackend(config=self.config, audio=None)
