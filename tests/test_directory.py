from __future__ import unicode_literals

import unittest

import pykka

from mopidy_podcast.directory import PodcastDirectory
from mopidy_podcast.controller import PodcastDirectoryController
from mopidy_podcast.models import Ref


class TestDirectory(PodcastDirectory):

    name = 'test'

    root_name = 'Test Directory'

    refs = [Ref.podcast(uri='/foo', name='bar')]

    def __init__(self, config):
        super(TestDirectory, self).__init__(config)

    def browse(self, uri, limit=None):
        return self.refs

    def search(self, uri, terms, attr=None, type=None, limit=None):
        return self.refs

    def refresh(self, uri=None):
        self.refs = [Ref.podcast(uri='/foo', name='baz')]


class DirectoryTest(unittest.TestCase):

    def setUp(self):
        self.directory = PodcastDirectoryController([TestDirectory({})])

    def tearDown(self):
        pykka.ActorRegistry.stop_all()

    def test_browse(self):
        self.assertItemsEqual(
            self.directory.browse(None),
            [Ref.directory(uri='podcast://test/', name='Test Directory')]
        )
        self.assertItemsEqual(
            self.directory.browse('podcast://test/'),
            [Ref.podcast(uri='podcast://test/foo', name='bar')]
        )

    def test_search(self):
        self.assertItemsEqual(
            self.directory.search(None, []),
            [Ref.podcast(uri='podcast://test/foo', name='bar')]
        )
        self.assertItemsEqual(
            self.directory.search('podcast://test/foo', []),
            [Ref.podcast(uri='podcast://test/foo', name='bar')]
        )

    def test_refresh(self):
        self.directory.refresh(),
        self.assertItemsEqual(
            self.directory.browse('podcast://test/'),
            [Ref.podcast(uri='podcast://test/foo', name='baz')]
        )
