from __future__ import unicode_literals

import unittest
import xml.etree.ElementTree

from mopidy_podcast.rssfeed import *  # noqa


def element(_=None, tag='', **kwargs):
    e = xml.etree.ElementTree.Element(tag, attrib=kwargs)
    e.text = _
    return e


def tree(tag, _=None, **kwargs):
    e = xml.etree.ElementTree.Element('root')
    e.append(element(_, tag=tag, **kwargs))
    return e


class RSSFeedTest(unittest.TestCase):

    def test_bool(self):
        self.assertFalse(to_bool(element()))
        self.assertFalse(to_bool(element('')))
        self.assertFalse(to_bool(element('foo')))
        self.assertFalse(to_bool(element('no')))
        self.assertTrue(to_bool(element('yes')))
        self.assertTrue(to_bool(element('YES')))

    def test_int(self):
        self.assertEqual(None, to_int(element()))
        self.assertEqual(None, to_int(element('')))
        self.assertEqual(None, to_int(element('foo')))
        self.assertEqual(0, to_int(element('0')))
        self.assertEqual(42, to_int(element('42')))

    def test_datetime(self):
        self.assertEqual(None, to_datetime(element()))
        self.assertEqual(None, to_datetime(element('')))
        self.assertEqual(None, to_datetime(element('foo')))
        self.assertEqual(
            '2014-06-01 19:00:00',
            str(to_datetime(element('Wed, 1 Jun 2014 19:00:00 GMT')))
        )

    def test_timedelta(self):
        self.assertEqual(None, to_timedelta(element()))
        self.assertEqual(None, to_timedelta(element('')))
        self.assertEqual(None, to_timedelta(element('foo')))
        self.assertEqual('0:03:59', str(to_timedelta(element('239'))))
        self.assertEqual('0:03:59', str(to_timedelta(element('239.0'))))
        self.assertEqual('0:03:59', str(to_timedelta(element('3:59'))))
        self.assertEqual('0:03:59', str(to_timedelta(element('3:59.0'))))
        self.assertEqual('0:03:59', str(to_timedelta(element('03:59'))))
        self.assertEqual('0:03:59', str(to_timedelta(element('03:59.0'))))
        self.assertEqual('0:03:59', str(to_timedelta(element('0:03:59'))))
        self.assertEqual('0:03:59', str(to_timedelta(element('0:03:59.0'))))

    def test_category(self):
        self.assertEqual(None, to_category(element()))
        self.assertEqual(None, to_category(element('')))
        self.assertEqual(None, to_category(element('foo')))
        self.assertEqual('Music', to_category(element(text='Music')))

    def test_gettag(self):
        self.assertEqual(None, gettag(tree('bar'), 'foo'))
        self.assertEqual(None, gettag(tree('foo'), 'foo'))
        self.assertEqual(None, gettag(tree('foo', None), 'foo'))
        self.assertEqual(None, gettag(tree('foo', ''), 'foo'))
        self.assertEqual('bar', gettag(tree('foo', 'bar'), 'foo'))
        self.assertEqual('bar', gettag(tree('foo', ' bar '), 'foo'))
        self.assertEqual('42', gettag(tree('foo', '42'), 'foo'))
        self.assertEqual(42, gettag(tree('foo', '42'), 'foo', to_int))
