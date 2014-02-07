"""
Podcast implementation according to
https://www.apple.com/itunes/podcasts/specs.html
"""
from __future__ import unicode_literals

import collections
import datetime
import logging
import re

DURATION_RE = re.compile(r"""
(?:
    (?:(?P<hours>\d+):)?
    (?P<minutes>\d+):
)?
(?P<seconds>\d+)
""", flags=re.VERBOSE)

NAMESPACES = {
    'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'
}

logger = logging.getLogger(__name__)


def _settagattr(self, name, item, tag, default=None, convert=None,
                namespaces=None):
    e = item.find(tag, namespaces=namespaces)
    if e is None:
        return setattr(self, name, default)
    elif convert is not None:
        return setattr(self, name, convert(e))
    else:
        return setattr(self, name, e.text.strip())


def _to_datetime(e):
    from email.utils import mktime_tz, parsedate_tz
    try:
        timestamp = mktime_tz(parsedate_tz(e.text))
    except AttributeError:
        logger.warn('Invalid podcast date element "%s"', e.text)
        return None
    except TypeError:
        logger.warn('Invalid podcast date element "%s"', e.text)
        return None
    return datetime.datetime.fromtimestamp(timestamp)


def _to_timedelta(e):
    try:
        groups = DURATION_RE.match(e.text).groupdict('0')
    except AttributeError:
        logger.warn('Invalid podcast duration element "%s"', e.text)
        return None
    except TypeError:
        logger.warn('Invalid podcast duration element "%s"', e.text)
        return None
    return datetime.timedelta(**{k: int(v) for k, v in groups.items()})


def _to_wordlist(e):
    return [s.strip() for s in e.text.split(',')]


class Podcast(collections.Sequence):

    def __init__(self, url):
        self.url = url
        self.update()

    def __getitem__(self, index):
        return self.episodes.__getitem__(index)

    def __iter__(self):
        return self.episodes.__iter__()

    def __len__(self):
        return self.episodes.__len__()

    def update(self):
        from urllib2 import urlopen
        import xml.etree.ElementTree as ET

        channel = ET.parse(urlopen(self.url)).find('channel')
        for name in ('title', 'link', 'description', 'language', 'copyright'):
            self._settagattr(name, channel, name)
        for name in ('author', 'complete', 'explicit', 'subtitle', 'summary'):
            self._settagattr(name, channel, 'itunes:' + name)
        self._settagattr('image', channel, 'itunes:image', lambda e: e.attrib)
        self._settagattr('keywords', channel, 'itunes:keywords', _to_wordlist)

        # self.category: first browse (top-level) category
        self._settagattr('category', channel, 'itunes:category',
                         lambda e: e.get('text'))
        # self.categories: {category: [sub-category, ...], ...}
        self.categories = {}
        for e in channel.iterfind('itunes:category', namespaces=NAMESPACES):
            subcats = e.iterfind('itunes:category', namespaces=NAMESPACES)
            self.categories[e.get('text')] = [i.get('text') for i in subcats]

        self.episodes = [Episode(item) for item in channel.iter(tag='item')]

    def _settagattr(self, name, item, tag, convert=None):
        _settagattr(self, name, item, tag, None, convert, NAMESPACES)


class Episode(object):

    def __init__(self, item):
        for name in ('title', 'link', 'description', 'guid'):
            self._settagattr(name, item, name)
        for name in ('author', 'block', 'explicit', 'subtitle', 'summary'):
            self._settagattr(name, item, 'itunes:' + name)
        self._settagattr('enclosure', item, 'enclosure', lambda e: e.attrib)
        self._settagattr('pubdate', item, 'pubDate', _to_datetime)
        self._settagattr('duration', item, 'itunes:duration', _to_timedelta)
        self._settagattr('keywords', item, 'itunes:keywords', _to_wordlist)
        self._settagattr('order', item, 'itunes:order', lambda e: int(e.text))

        # normalization/fallbacks
        if not self.guid and self.enclosure:
            self.guid = self.enclosure.get('url')

    def _settagattr(self, name, item, tag, convert=None):
        _settagattr(self, name, item, tag, None, convert, NAMESPACES)


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('url', metavar='URL', help='Podcast URL')
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-n', '--no-episodes', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    podcast = Podcast(args.url)

    if args.verbose:
        print '\n%12s: %s' % ('URL', podcast.url)
        for name in ('title', 'link', 'description', 'language', 'copyright'):
            print '%12s: %s' % (name.title(), getattr(podcast, name))
        for name in ('author', 'complete', 'explicit', 'subtitle', 'summary'):
            print '%12s: %s' % (name.title(), getattr(podcast, name))
        for name in ('image', 'keywords', 'category', 'categories'):
            print '%12s: %s' % (name.title(), getattr(podcast, name))
    else:
        print "%s [%s]" % (podcast.title, podcast.author)

    if args.no_episodes:
        sys.exit(0)

    for index, episode in enumerate(podcast):
        if args.verbose:
            print '\n%12s: #%d [%r]' % ('Episode', index + 1, episode.order)
            for name in ('title', 'link', 'description', 'guid'):
                print '%12s: %s' % (name.title(), getattr(episode, name))
            for name in ('author', 'block', 'explicit', 'subtitle', 'summary'):
                print '%12s: %s' % (name.title(), getattr(episode, name))
            for name in ('enclosure', 'pubdate', 'duration', 'keywords'):
                print '%12s: %s' % (name.title(), getattr(episode, name))
        else:
            print '#%d: [%s] %s' % (index + 1, episode.pubdate, episode.title)
