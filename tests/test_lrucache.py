from __future__ import unicode_literals
import unittest

from mopidy_podcast.lrucache import LRUCache


class LRUCacheTest(unittest.TestCase):

    def test_insert(self):
        cache = LRUCache(maxsize=2, ttl=3600)
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        self.assertEqual(cache['b'], 2)
        self.assertEqual(cache['c'], 3)
        self.assertNotIn('a', cache)

        cache['a'] = 4
        self.assertEqual(cache['a'], 4)
        self.assertEqual(cache['c'], 3)
        self.assertNotIn('b', cache)

        cache['b'] = 5
        self.assertEqual(cache['b'], 5)
        self.assertEqual(cache['c'], 3)
        self.assertNotIn('a', cache)

    def test_expire(self):
        cache = LRUCache(maxsize=2, ttl=0)
        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        with self.assertRaises(KeyError):
            cache['a']
        with self.assertRaises(KeyError):
            cache['b']
        with self.assertRaises(KeyError):
            cache['c']
