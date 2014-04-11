from __future__ import unicode_literals

import unittest

import pykka

from mopidy_podcast.directory import PodcastDirectory
from mopidy_podcast.controller import PodcastDirectoryController
from mopidy_podcast.models import Ref


class TestDirectory(PodcastDirectory):

    name = 'test'

    display_name = 'Test Directory'

    def __init__(self, config, timeout):
        super(TestDirectory, self).__init__(config, timeout)
        self.dirs = [Ref.directory(uri='foo', name='bar')]

    def browse(self, uri, limit=None):
        return self.dirs

    def search(self, terms=None, attribute=None, type=None, limit=None):
        return [Ref.podcast(uri='foo', name='bar')]

    def update(self):
        self.dirs = [Ref.directory(uri='foo', name='baz')]


class DirectoryTest(unittest.TestCase):

    def setUp(self):
        self.directory = PodcastDirectoryController({
            'podcast': {
                'cache_size': 1,
                'cache_ttl': 1
            }
        }, None, [TestDirectory])

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_browse(self):
        self.assertItemsEqual(
            self.directory.browse(None),
            [Ref.directory(uri='//test/', name='Test Directory')]
        )
        self.assertItemsEqual(
            self.directory.browse('//test/'),
            [Ref.directory(uri='//test/foo', name='bar')]
        )

    def test_search(self):
        self.assertItemsEqual(
            self.directory.search(),
            [Ref.podcast(uri='//test/foo', name='bar')]
        )

    def test_update(self):
        self.assertItemsEqual(
            self.directory.browse('//test/'),
            [Ref.directory(uri='//test/foo', name='bar')]
        )
        self.directory.update(),
        self.assertItemsEqual(
            self.directory.browse('//test/'),
            [Ref.directory(uri='//test/foo', name='baz')]
        )
