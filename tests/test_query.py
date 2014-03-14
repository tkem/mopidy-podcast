from __future__ import unicode_literals

import unittest

from mopidy.models import Artist, Album, Track, Ref
from mopidy_podcast.query import Query


def anycase(*strings):
    return [s.upper() for s in strings] + [s.lower() for s in strings]


class QueryTest(unittest.TestCase):

    def assertQueryMatches(self, model, **kwargs):
        query = Query(kwargs, exact=False)
        self.assertTrue(query.match(model))

    def assertNotQueryMatches(self, model, **kwargs):
        query = Query(kwargs, exact=False)
        self.assertFalse(query.match(model))

    def assertQueryMatchesExact(self, model, **kwargs):
        query = Query(kwargs, exact=True)
        self.assertTrue(query.match(model))

    def assertNotQueryMatchesExact(self, model, **kwargs):
        query = Query(kwargs, exact=True)
        self.assertFalse(query.match(model))

    def test_create_query(self):
        for exact in (True, False):
            q1 = Query(dict(any='foo'), exact)
            self.assertEqual(q1.exact, exact)
            self.assertEqual(len(q1), 1)
            self.assertItemsEqual(q1, ['any'])
            self.assertEqual(len(q1['any']), 1)
            self.assertEqual(q1['any'][0], 'foo')
            self.assertNotEqual(q1['any'][0], 'bar')

            q2 = Query(dict(any=['foo', 'bar'], artist='x'), exact)
            self.assertEqual(q2.exact, exact)
            self.assertEqual(len(q2), 2)
            self.assertItemsEqual(q2, ['any', 'artist'])
            self.assertEqual(len(q2['any']), 2)
            self.assertEqual(len(q2['artist']), 1)
            self.assertEqual(q2['any'][0], 'foo')
            self.assertEqual(q2['any'][1], 'bar')
            self.assertEqual(q2['artist'][0], 'x')

    def test_query_errors(self):
        for exact in (True, False):
            with self.assertRaises(LookupError):
                Query(None, exact)
            with self.assertRaises(LookupError):
                Query({}, exact)
            with self.assertRaises(LookupError):
                Query({'artist': None}, exact)
            with self.assertRaises(LookupError):
                Query({'artist': ''}, exact)
            with self.assertRaises(LookupError):
                Query({'artist': []}, exact)
            with self.assertRaises(LookupError):
                Query({'artist': ['']}, exact)
            with self.assertRaises(LookupError):
                Query({'any': None}, exact)
            with self.assertRaises(LookupError):
                Query({'any': ''}, exact)
            with self.assertRaises(LookupError):
                Query({'any': []}, exact)
            with self.assertRaises(LookupError):
                Query({'any': ['']}, exact)
            with self.assertRaises(LookupError):
                Query({'foo': 'bar'}, exact)
            with self.assertRaises(TypeError):
                q = Query(dict(any='foo'), exact)
                q.match(Ref(name='foo'))

    def test_match_artist(self):
        artist = Artist(name='foo')

        for name in anycase('f', 'o', 'fo', 'oo', 'foo'):
            self.assertQueryMatches(artist, any=name)
            self.assertQueryMatches(artist, artist=name)

        self.assertQueryMatchesExact(artist, any='foo')
        self.assertQueryMatchesExact(artist, artist='foo')

        self.assertNotQueryMatches(artist, any='none')
        self.assertNotQueryMatches(artist, artist='none')

        self.assertNotQueryMatchesExact(artist, any='none')
        self.assertNotQueryMatchesExact(artist, artist='none')

    def test_match_album(self):
        artist = Artist(name='foo')
        album = Album(name='bar', artists=[artist])

        for name in anycase('f', 'o', 'fo', 'oo', 'foo'):
            self.assertQueryMatches(album, any=name)
            self.assertQueryMatches(album, artist=name)
            self.assertQueryMatches(album, albumartist=name)
        for name in anycase('b', 'a', 'ba', 'ar', 'bar'):
            self.assertQueryMatches(album, any=name)
            self.assertQueryMatches(album, album=name)

        self.assertQueryMatchesExact(album, any='foo')
        self.assertQueryMatchesExact(album, artist='foo')
        self.assertQueryMatchesExact(album, albumartist='foo')
        self.assertQueryMatchesExact(album, any='bar')
        self.assertQueryMatchesExact(album, album='bar')

        self.assertNotQueryMatches(album, any='none')
        self.assertNotQueryMatches(album, artist='bar')
        self.assertNotQueryMatches(album, album='foo')

        self.assertNotQueryMatchesExact(album, any='none')
        self.assertNotQueryMatchesExact(album, artist='bar')
        self.assertNotQueryMatchesExact(album, album='foo')

    def test_match_track(self):
        artist = Artist(name='foo')
        album = Album(name='bar', artists=[Artist(name='v/a')])
        track = Track(name='zyx', album=album, artists=[artist])

        for name in anycase('f', 'o', 'fo', 'oo', 'foo'):
            self.assertQueryMatches(track, any=name)
            self.assertQueryMatches(track, artist=name)
        for name in anycase('b', 'a', 'ba', 'ar', 'bar'):
            self.assertQueryMatches(track, any=name)
            self.assertQueryMatches(track, album=name)
        for name in anycase('v', '/', 'v/', '/a', 'v/a'):
            self.assertQueryMatches(track, any=name)
            self.assertQueryMatches(track, albumartist=name)
        for name in anycase('z', 'y', 'zy', 'yx', 'zyx'):
            self.assertQueryMatches(track, any=name)
            self.assertQueryMatches(track, track_name=name)

        self.assertQueryMatchesExact(track, any='foo')
        self.assertQueryMatchesExact(track, artist='foo')
        self.assertQueryMatchesExact(track, any='bar')
        self.assertQueryMatchesExact(track, album='bar')
        self.assertQueryMatchesExact(track, any='v/a')
        self.assertQueryMatchesExact(track, albumartist='v/a')
        self.assertQueryMatchesExact(track, any='zyx')
        self.assertQueryMatchesExact(track, track_name='zyx')

        self.assertNotQueryMatches(track, any='none')
        self.assertNotQueryMatches(track, artist='bar')
        self.assertNotQueryMatches(track, album='foo')
        self.assertNotQueryMatches(track, albumartist='zyx')
        self.assertNotQueryMatches(track, track_name='v/a')

        self.assertNotQueryMatchesExact(track, any='none')
        self.assertNotQueryMatchesExact(track, artist='bar')
        self.assertNotQueryMatchesExact(track, album='foo')
        self.assertNotQueryMatchesExact(track, albumartist='zyx')
        self.assertNotQueryMatchesExact(track, track_name='v/a')
