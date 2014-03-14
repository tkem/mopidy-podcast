from __future__ import unicode_literals

import unittest

from mopidy_podcast import Extension


class ExtensionTest(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()
        config = ext.get_default_config()
        self.assertIn('[podcast]', config)
        self.assertIn('enabled = true', config)

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()
        self.assertIn('directories', schema)
        self.assertIn('browse_label', schema)
        self.assertIn('search_limit', schema)
        self.assertIn('max_episodes', schema)
        self.assertIn('sort_order', schema)
        self.assertIn('update_interval', schema)
        self.assertIn('cache_size', schema)
        self.assertIn('cache_ttl', schema)
        self.assertIn('timeout', schema)
        self.assertIn('feeds', schema)
        self.assertIn('feeds_label', schema)
