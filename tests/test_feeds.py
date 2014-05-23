from __future__ import unicode_literals

import unittest

from mopidy_podcast.feeds import FeedsDirectory
from . import datapath

BASE_URL = 'http://example.com/podcasts/everything/'
LINK_URL = 'http://www.example.com/podcasts/everything/index.html'
IMAGE_URL = BASE_URL + 'AllAboutEverything.jpg'

EPISODE1_MEDIA_URL = BASE_URL + 'AllAboutEverythingEpisode1.mp3'
EPISODE1_IMAGE_URL = BASE_URL + 'AllAboutEverything/Episode3.jpg'  # sic!
EPISODE2_MEDIA_URL = BASE_URL + 'AllAboutEverythingEpisode2.mp3'
EPISODE2_IMAGE_URL = BASE_URL + 'AllAboutEverything/Episode2.jpg'
EPISODE3_MEDIA_URL = BASE_URL + 'AllAboutEverythingEpisode3.m4a'
EPISODE3_IMAGE_URL = BASE_URL + 'AllAboutEverything/Episode1.jpg'  # sic!

URI_PREFIX = BASE_URL + 'AllAboutEverything'


class FeedsTest(unittest.TestCase):

    def setUp(self):
        self.feeds = FeedsDirectory({
            'podcast': {
                'feeds': [],
                'feeds_root_name': 'Feeds',
                'feeds_cache_size': 1,
                'feeds_cache_ttl': 0,
                'feeds_timeout': None
            }
        })

    def test_parse(self):
        feedurl = 'file://' + datapath('example.xml')
        podcast = self.feeds.get(feedurl)
        self.assertEqual(podcast.uri, feedurl)

        self.assertEqual(podcast.title, 'All About Everything')
        self.assertEqual(podcast.link, LINK_URL)
        self.assertRegexpMatches(podcast.summary, '^All About Everything')
        self.assertEqual(podcast.language, 'en-us')
        self.assertRegexpMatches(podcast.copyright, 'John Doe & Family')
        self.assertEqual(podcast.pubdate, None)
        self.assertEqual(podcast.image.uri, IMAGE_URL)

        self.assertEqual(podcast.author, 'John Doe')
        self.assertEqual(podcast.complete, None)
        self.assertEqual(podcast.explicit, None)
        self.assertEqual(podcast.subtitle, 'A show about everything')
        self.assertEqual(podcast.category, 'Technology')

        self.assertEqual(len(podcast.episodes), 3)
        episode3, episode2, episode1 = podcast.episodes

        # episode 1

        self.assertEqual(episode1.uri, podcast.uri + '#' + EPISODE1_MEDIA_URL)
        self.assertEqual(episode1.title, 'Red, Whine, & Blue')
        self.assertEqual(episode1.author, 'Various')
        self.assertEqual(str(episode1.pubdate), '2005-06-01 19:00:00')
        self.assertEqual(str(episode1.duration), '0:03:59')
        self.assertEqual(episode1.enclosure.uri, EPISODE1_MEDIA_URL)
        self.assertEqual(episode1.image.uri, EPISODE1_IMAGE_URL)
        self.assertRegexpMatches(episode1.subtitle, '^Red \+ Blue')
        self.assertRegexpMatches(episode1.summary, '^This week')

        # episode 2

        self.assertEqual(episode2.uri, podcast.uri + '#' + EPISODE2_MEDIA_URL)
        self.assertEqual(episode2.title, 'Socket Wrench Shootout')
        self.assertEqual(episode2.author, 'Jane Doe')
        self.assertEqual(str(episode2.pubdate), '2005-06-08 19:00:00')
        self.assertEqual(str(episode2.duration), '0:04:34')
        self.assertEqual(episode2.enclosure.uri, EPISODE2_MEDIA_URL)
        self.assertEqual(episode2.image.uri, EPISODE2_IMAGE_URL)
        self.assertRegexpMatches(episode2.subtitle, '^Comparing socket')
        self.assertRegexpMatches(episode2.summary, '^This week')

        # episode 3

        self.assertEqual(episode3.uri, podcast.uri + '#' + EPISODE3_MEDIA_URL)
        self.assertEqual(episode3.title, 'Shake Shake Shake Your Spices')
        self.assertEqual(episode3.author, 'John Doe')
        self.assertEqual(str(episode3.pubdate), '2005-06-15 19:00:00')
        self.assertEqual(str(episode3.duration), '0:07:04')
        self.assertEqual(episode3.enclosure.uri, EPISODE3_MEDIA_URL)
        self.assertEqual(episode3.image.uri, EPISODE3_IMAGE_URL)
        self.assertRegexpMatches(episode3.summary, '^This week')
        self.assertRegexpMatches(episode3.subtitle, '^A short primer')
