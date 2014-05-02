from __future__ import unicode_literals

import unittest

from mopidy_podcast.models import Podcast
from datetime import timedelta
from . import datapath

BASE_URL = 'http://example.com/podcasts/everything/'
FEED_URL = BASE_URL + 'example.xml'
IMAGE_URL = BASE_URL + 'AllAboutEverything.jpg'
EPISODE1_MEDIA_URL = BASE_URL + 'AllAboutEverythingEpisode1.mp3'
EPISODE1_IMAGE_URL = BASE_URL + 'AllAboutEverything/Episode3.jpg'  # sic!
EPISODE2_MEDIA_URL = BASE_URL + 'AllAboutEverythingEpisode2.mp3'
EPISODE2_IMAGE_URL = BASE_URL + 'AllAboutEverything/Episode2.jpg'
EPISODE3_MEDIA_URL = BASE_URL + 'AllAboutEverythingEpisode3.m4a'
EPISODE3_IMAGE_URL = BASE_URL + 'AllAboutEverything/Episode1.jpg'  # sic!


LINK_URL = 'http://www.example.com/podcasts/everything/index.html'

URI_PREFIX = BASE_URL + 'AllAboutEverything'


class ModelsTest(unittest.TestCase):

    def test_parse(self):
        with open(datapath('example.xml')) as f:
            podcast = Podcast.parse(f, FEED_URL)
        self.assertEqual(podcast.uri, FEED_URL)
        self.assertEqual(podcast.title, 'All About Everything')
        self.assertEqual(podcast.link, LINK_URL)
        self.assertRegexpMatches(podcast.description, '^All About Everything')
        self.assertEqual(podcast.language, 'en-us')
        self.assertRegexpMatches(podcast.copyright, 'John Doe & Family')
        self.assertEqual(podcast.pubdate, None)
        self.assertEqual(podcast.image.uri, IMAGE_URL)

        self.assertEqual(podcast.author, 'John Doe')
        self.assertEqual(podcast.complete, None)
        self.assertEqual(podcast.explicit, None)
        self.assertEqual(podcast.subtitle, 'A show about everything')
        self.assertItemsEqual(podcast.keywords, [])
        self.assertEqual(podcast.category, 'Technology')

        self.assertEqual(len(podcast.episodes), 3)
        episode3, episode2, episode1 = podcast.episodes

        # episode 1

        self.assertEqual(episode1.uri, FEED_URL + '#' + EPISODE1_MEDIA_URL)
        self.assertEqual(episode1.title, 'Red, Whine, & Blue')
        self.assertEqual(episode1.link, None)
        self.assertEqual(episode1.description, None)
        #self.assertEqual(episode1.pubdate, 'Wed, 1 Jun 2005 19:00:00 GMT')
        self.assertEqual(episode1.enclosure.uri, EPISODE1_MEDIA_URL)

        self.assertEqual(episode1.author, 'Various')
        self.assertEqual(episode1.image.uri, EPISODE1_IMAGE_URL)
        self.assertEqual(episode1.explicit, None)
        self.assertEqual(episode1.subtitle, 'Red + Blue != Purple')
        self.assertEqual(episode1.duration, timedelta(minutes=3, seconds=59))
        self.assertItemsEqual(episode1.keywords, [])
        self.assertEqual(episode1.order, None)

        # episode 2

        self.assertEqual(episode2.uri, FEED_URL + '#' + EPISODE2_MEDIA_URL)
        self.assertEqual(episode2.title, 'Socket Wrench Shootout')
        self.assertEqual(episode2.link, None)
        self.assertEqual(episode2.description, None)
        #self.assertEqual(episode2.pubdate, 'Wed, 8 Jun 2005 19:00:00 GMT')
        self.assertEqual(episode2.enclosure.uri, EPISODE2_MEDIA_URL)

        self.assertEqual(episode2.author, 'Jane Doe')
        self.assertEqual(episode2.image.uri, EPISODE2_IMAGE_URL)
        self.assertEqual(episode2.explicit, None)
        self.assertRegexpMatches(episode2.subtitle, '^Comparing socket')
        self.assertEqual(episode2.duration, timedelta(minutes=4, seconds=34))
        self.assertItemsEqual(episode2.keywords, [])
        self.assertEqual(episode2.order, None)

        # episode 3

        self.assertEqual(episode3.uri, FEED_URL + '#' + EPISODE3_MEDIA_URL)
        self.assertEqual(episode3.title, 'Shake Shake Shake Your Spices')
        self.assertEqual(episode3.link, None)
        self.assertEqual(episode3.description, None)
        #self.assertEqual(episode3.pubdate, 'Wed, 15 Jun 2005 19:00:00 GMT')
        self.assertEqual(episode3.enclosure.uri, EPISODE3_MEDIA_URL)

        self.assertEqual(episode3.author, 'John Doe')
        self.assertEqual(episode3.image.uri, EPISODE3_IMAGE_URL)
        self.assertEqual(episode3.explicit, None)
        self.assertRegexpMatches(episode3.subtitle, '^A short primer')
        self.assertEqual(episode3.duration, timedelta(minutes=7, seconds=4))
        self.assertItemsEqual(episode3.keywords, [])
        self.assertEqual(episode3.order, None)
