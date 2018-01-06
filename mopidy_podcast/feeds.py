from __future__ import unicode_literals

import datetime
import email.utils
import re

from mopidy import models

import uritools

from . import Extension

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


def parse(source):
    if isinstance(source, basestring):
        url = uritools.uricompose('file', '', source)
    else:
        url = source.geturl()
    root = ElementTree.parse(source).getroot()
    if root.tag == 'rss':
        return RssFeed(url, root)
    elif root.tag == 'opml':
        return OpmlFeed(url, root)
    else:
        raise TypeError('Not a recognized podcast feed: %s', url)


def get_attrib(element, attrib, default=None):
    """
    Case-insensitive get for xml.etree.ElementTree.Element objects.

    The OPML spec is ambiguous on the subject of case-sensitivity so we can't
    assume keys will be lowercase.
    """
    return element.get(
            attrib,
            element.get(
                attrib.upper(),
                element.get(
                    attrib.lower(), default
                )
            )
        )


class PodcastFeed(object):

    def __init__(self, url):
        self.uri = self.getfeeduri(url)

    @classmethod
    def getfeeduri(cls, url):
        return uritools.uridefrag(Extension.ext_name + '+' + url).uri

    def getitemuri(self, guid, safe=uritools.SUB_DELIMS+b':@/?'):
        return self.uri + '#' + uritools.uriencode(guid, safe=safe)

    def getstreamuri(self, guid):
        raise NotImplemented

    def items(self, newest_first=None):
        raise NotImplemented

    def tracks(self, newest_first=None):
        return []

    def images(self):
        return []


class RssFeed(PodcastFeed):

    ITUNES_PREFIX = '{http://www.itunes.com/dtds/podcast-1.0.dtd}'

    DURATION_RE = re.compile(r"""
    (?:
      (?:(?P<hours>\d+):)?
      (?P<minutes>\d+):
    )?
    (?P<seconds>\d+)
    """, flags=re.VERBOSE)

    def __init__(self, url, root):
        super(RssFeed, self).__init__(url)
        self.__channel = channel = root.find('channel')
        items = channel.findall('./item/enclosure[@url]/..')
        self.__items = list(sorted(items, key=self.__order))

    def getstreamuri(self, guid):
        for item in self.__items:
            if self.__guid(item) == guid:
                return get_attrib(item.find('enclosure'), 'url')
        return None

    def items(self, newest_first=False):
        for item in (reversed(self.__items) if newest_first else self.__items):
            yield models.Ref.track(
                uri=self.getitemuri(self.__guid(item)),
                name=item.findtext('title')
            )

    def tracks(self, newest_first=False):
        album = models.Album(
            uri=self.uri,
            name=self.__channel.findtext('title'),
            artists=self.__artists(self.__channel),
            num_tracks=len(self.__items)
        )
        genre = self.__genre(self.__channel)
        items = enumerate(self.__items, start=1)
        for index, item in (reversed(list(items)) if newest_first else items):
            yield models.Track(
                uri=self.getitemuri(self.__guid(item)),
                name=item.findtext('title'),
                album=album,
                artists=(self.__artists(item) or album.artists),
                genre=genre,
                date=self.__date(item),
                length=self.__length(item),
                comment=item.findtext('description'),
                track_no=index
            )

    def images(self):
        image = self.__image(self.__channel)
        default = [image] if image else None
        if default:
            yield self.uri, default
        for item in self.__items:
            image = self.__image(item)
            if image:
                yield self.getitemuri(self.__guid(item)), [image]
            elif default:
                yield self.getitemuri(self.__guid(item)), default
            else:
                pass

    @classmethod
    def __artists(cls, etree):
        elem = etree.find(cls.ITUNES_PREFIX + 'author')
        if elem is not None:
            return [models.Artist(name=elem.text)]
        else:
            return None

    @classmethod
    def __date(cls, etree):
        text = etree.findtext('pubDate')
        try:
            timestamp = email.utils.mktime_tz(email.utils.parsedate_tz(text))
        except AttributeError:
            return None
        except TypeError:
            return None
        else:
            return datetime.datetime.utcfromtimestamp(
                timestamp,
            ).date().isoformat()

    @classmethod
    def __genre(cls, etree):
        elem = etree.find(cls.ITUNES_PREFIX + 'category')
        if elem is not None:
            return get_attrib(elem, 'text')
        else:
            return None

    @classmethod
    def __guid(cls, etree):
        return (etree.findtext('guid') or
                get_attrib(etree.find('enclosure'), 'url'))

    @classmethod
    def __image(cls, etree):
        elem = etree.find(cls.ITUNES_PREFIX + 'image')
        if elem is not None:
            return models.Image(uri=get_attrib(elem, 'href'))
        else:
            return None

    @classmethod
    def __length(cls, etree):
        text = etree.findtext(cls.ITUNES_PREFIX + 'duration')
        try:
            groups = cls.DURATION_RE.match(text).groupdict('0')
        except AttributeError:
            return None
        except TypeError:
            return None
        else:
            d = datetime.timedelta(**{k: int(v) for k, v in groups.items()})
            return int(d.total_seconds() * 1000)

    @staticmethod
    def __order(etree):
        text = etree.findtext('pubDate')
        try:
            timestamp = email.utils.mktime_tz(email.utils.parsedate_tz(text))
        except AttributeError:
            return 0
        except TypeError:
            return 0
        else:
            return timestamp


class OpmlFeed(PodcastFeed):  # not really a "feed"

    TYPES = {
        'include': lambda e: models.Ref.directory(
            name=get_attrib(e, 'text'),
            uri=PodcastFeed.getfeeduri(get_attrib(e, 'url'))
        ),
        'link': lambda e: models.Ref(
            type=(
                models.Ref.DIRECTORY
                if get_attrib(e, 'url').endswith('.opml')
                else models.Ref.ALBUM
            ),
            name=get_attrib(e, 'text'),
            uri=PodcastFeed.getfeeduri(get_attrib(e, 'url'))
        ),
        'rss': lambda e: models.Ref.album(
            name=get_attrib(e, 'title', default=get_attrib(e, 'text')),
            uri=PodcastFeed.getfeeduri(get_attrib(e, 'xmlUrl'))
        )
    }

    def __init__(self, url, root):
        super(OpmlFeed, self).__init__(url)
        self.__outlines = root.findall('./body//outline[@type]')

    def items(self, newest_first=None):
        for e in self.__outlines:
            try:
                ref = self.TYPES[get_attrib(e, 'type').lower()]
            except KeyError:
                pass
            else:
                yield ref(e)


if __name__ == '__main__':  # pragma: no cover
    import argparse
    import contextlib
    import json
    import urllib2
    import sys

    from mopidy.models import ModelJSONEncoder

    parser = argparse.ArgumentParser()
    parser.add_argument('url', metavar='URL')
    parser.add_argument('-i', '--images', action='store_true')
    parser.add_argument('-t', '--tracks', action='store_true')
    args = parser.parse_args()

    with contextlib.closing(urllib2.urlopen(args.url)) as source:
        feed = PodcastFeed.parse(source)
    if args.tracks:
        result = list(feed.tracks())
    elif args.images:
        result = dict(feed.images())
    else:
        result = list(feed.items())
    json.dump(result, sys.stdout, cls=ModelJSONEncoder, indent=2)
    sys.stdout.write('\n')
