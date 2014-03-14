from __future__ import unicode_literals

import unittest

from mopidy_podcast.models import Podcast
from datetime import timedelta
from . import datapath


class ModelsTest(unittest.TestCase):

    def test_parse(self):
        with open(datapath('example.xml')) as f:
            podcast = Podcast.parse(f)
        self.assertEqual(podcast.title, 'All About Everything')
        self.assertRegexpMatches(podcast.link, '^http://www.example.com')
        self.assertRegexpMatches(podcast.description, '^All About Everything')
        self.assertEqual(podcast.language, 'en-us')
        self.assertRegexpMatches(podcast.copyright, 'John Doe & Family')
        self.assertEqual(podcast.pubdate, None)
        self.assertEqual(podcast.image, None)

        self.assertEqual(podcast.author, 'John Doe')
        self.assertEqual(podcast.complete, None)
        self.assertEqual(podcast.explicit, None)
        self.assertEqual(podcast.subtitle, 'A show about everything')
        self.assertRegexpMatches(podcast.summary, '^All About Everything')
        self.assertItemsEqual(podcast.keywords, [])
        self.assertEqual(podcast.category, 'Technology')

        self.assertEqual(len(podcast.episodes), 3)
        episode3, episode2, episode1 = podcast.episodes

        self.assertEqual(episode3.title, 'Shake Shake Shake Your Spices')
        self.assertEqual(episode3.link, None)
        self.assertEqual(episode3.description, None)
        self.assertRegexpMatches(episode3.guid, '/aae20050615.m4a$')
        #self.assertEqual(episode3.pubdate, 'Wed, 15 Jun 2005 19:00:00 GMT')
        self.assertRegexpMatches(episode3.enclosure.url, 'Episode3.m4a$')

        self.assertEqual(episode3.author, 'John Doe')
        self.assertEqual(episode3.block, None)
        self.assertEqual(episode3.explicit, None)
        self.assertRegexpMatches(episode3.subtitle, '^A short primer')
        self.assertRegexpMatches(episode3.summary, 'salt and pepper shakers')
        self.assertEqual(episode3.duration, timedelta(minutes=7, seconds=4))
        self.assertItemsEqual(episode3.keywords, [])
        self.assertEqual(episode3.order, None)

        self.assertEqual(episode2.title, 'Socket Wrench Shootout')
        self.assertEqual(episode2.link, None)
        self.assertEqual(episode2.description, None)
        self.assertRegexpMatches(episode2.guid, '/aae20050608.mp3$')
        #self.assertEqual(episode2.pubdate, 'Wed, 8 Jun 2005 19:00:00 GMT')
        self.assertRegexpMatches(episode2.enclosure.url, 'Episode2.mp3$')

        self.assertEqual(episode2.author, 'Jane Doe')
        self.assertEqual(episode2.block, None)
        self.assertEqual(episode2.explicit, None)
        self.assertRegexpMatches(episode2.subtitle, '^Comparing socket')
        self.assertRegexpMatches(episode2.summary, 'socket wrenches')
        self.assertEqual(episode2.duration, timedelta(minutes=4, seconds=34))
        self.assertItemsEqual(episode2.keywords, [])
        self.assertEqual(episode2.order, None)

        self.assertEqual(episode1.title, 'Red, Whine, & Blue')
        self.assertEqual(episode1.link, None)
        self.assertEqual(episode1.description, None)
        self.assertRegexpMatches(episode1.guid, '/aae20050601.mp3$')
        #self.assertEqual(episode1.pubdate, 'Wed, 1 Jun 2005 19:00:00 GMT')
        self.assertRegexpMatches(episode1.enclosure.url, 'Episode1.mp3$')

        self.assertEqual(episode1.author, 'Various')
        self.assertEqual(episode1.block, None)
        self.assertEqual(episode1.explicit, None)
        self.assertEqual(episode1.subtitle, 'Red + Blue != Purple')
        self.assertRegexpMatches(episode1.summary, 'surviving')
        self.assertEqual(episode1.duration, timedelta(minutes=3, seconds=59))
        self.assertItemsEqual(episode1.keywords, [])
        self.assertEqual(episode1.order, None)
