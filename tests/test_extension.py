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
        self.assertIn('feed_urls', schema)
        self.assertIn('browse_label', schema)
        self.assertIn('update_interval', schema)
        self.assertIn('sort_order', schema)
