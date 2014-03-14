from __future__ import unicode_literals

import unittest

import pykka

from mopidy_podcast import PodcastDirectory
from mopidy_podcast.directory import PodcastDirectoryController
from mopidy_podcast.models import Ref


class TestDirectory(PodcastDirectory):

    name = 'test'

    display_name = 'Test Directory'

    def __init__(self, backend):
        super(TestDirectory, self).__init__(backend)
        self.dirs = [Ref.directory(uri='foo', name='bar')]

    def browse(self, uri):
        return self.dirs

    def search(self, terms=None, attribute=None, limit=None):
        return [Ref.podcast(uri='foo', name='bar')]

    def refresh(self, uri=None):
        self.dirs = [Ref.directory(uri='foo', name='baz')]


class DirectoryTest(unittest.TestCase):

    def setUp(self):
        self.directory = PodcastDirectoryController(None, [TestDirectory])

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_browse(self):
        self.assertItemsEqual(
            self.directory.browse(None),
            [Ref.directory(uri='podcast://test/', name='Test Directory')]
        )
        self.assertItemsEqual(
            self.directory.browse('podcast://test/'),
            [Ref.directory(uri='podcast://test/foo', name='bar')]
        )

    def test_search(self):
        self.assertItemsEqual(
            self.directory.search(),
            [Ref.podcast(uri='podcast://test/foo', name='bar')]
        )

    def test_refresh(self):
        self.assertItemsEqual(
            self.directory.browse('podcast://test/'),
            [Ref.directory(uri='podcast://test/foo', name='bar')]
        )
        self.directory.refresh(),
        self.assertItemsEqual(
            self.directory.browse('podcast://test/'),
            [Ref.directory(uri='podcast://test/foo', name='baz')]
        )
