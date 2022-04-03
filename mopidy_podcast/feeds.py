import datetime
import email.utils
import re

import uritools
from mopidy import models

from . import Extension

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


def parse(source):
    if isinstance(source, str):
        url = uritools.uricompose("file", "", source)
    else:
        url = source.geturl()
    root = ElementTree.parse(source).getroot()
    if root.tag == "rss":
        return RssFeed(url, root)
    elif root.tag == "opml":
        return OpmlFeed(url, root)
    else:
        raise TypeError("Not a recognized podcast feed: %s", url)


def get_url(source, default=None):
    """
    Get URL from xml.etree.ElementTree.Element.

    URL is often capitalized in OPML feeds.
    """
    return source.get("url", source.get("URL", default))


class PodcastFeed:
    def __init__(self, url):
        self.uri = self.getfeeduri(url)

    @classmethod
    def getfeeduri(cls, url):
        return uritools.uridefrag(Extension.ext_name + "+" + url).uri

    def getitemuri(self, guid, safe=uritools.SUB_DELIMS + ":@/?"):
        return self.uri + "#" + uritools.uriencode(guid, safe=safe).decode()

    def getstreamuri(self, guid):
        raise NotImplementedError

    def items(self, newest_first=None):
        raise NotImplementedError

    def tracks(self, newest_first=None):
        return []

    def images(self):
        return []


class RssFeed(PodcastFeed):

    ITUNES_PREFIX = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"

    DURATION_RE = re.compile(
        r"""
    (?:
      (?:(?P<hours>\d+):)?
      (?P<minutes>\d+):
    )?
    (?P<seconds>\d+)
    """,
        flags=re.VERBOSE,
    )

    def __init__(self, url, root):
        super().__init__(url)
        self.__channel = channel = root.find("channel")
        items = channel.findall("./item/enclosure[@url]/..")
        self.__items = list(sorted(items, key=self.__order))

    def getstreamuri(self, guid):
        for item in self.__items:
            if self.__guid(item) == guid:
                return get_url(item.find("enclosure"))
        return None

    def items(self, newest_first=False):
        for item in reversed(self.__items) if newest_first else self.__items:
            yield models.Ref.track(
                uri=self.getitemuri(self.__guid(item)),
                name=item.findtext("title"),
            )

    def tracks(self, newest_first=False):
        album = models.Album(
            uri=self.uri,
            name=self.__channel.findtext("title"),
            artists=self.__artists(self.__channel),
            num_tracks=len(self.__items),
        )
        genre = self.__genre(self.__channel)
        items = enumerate(self.__items, start=1)
        for index, item in reversed(list(items)) if newest_first else items:
            yield models.Track(
                uri=self.getitemuri(self.__guid(item)),
                name=item.findtext("title"),
                album=album,
                artists=(self.__artists(item) or album.artists),
                genre=genre,
                date=self.__date(item),
                length=self.__length(item),
                comment=item.findtext("description"),
                track_no=index,
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
        elem = etree.find(cls.ITUNES_PREFIX + "author")
        if elem is not None and elem.text:
            return [models.Artist(name=elem.text)]
        else:
            return None

    @classmethod
    def __date(cls, etree):
        text = etree.findtext("pubDate")
        try:
            timestamp = email.utils.mktime_tz(email.utils.parsedate_tz(text))
        except AttributeError:
            return None
        except TypeError:
            return None
        else:
            return (
                datetime.datetime.utcfromtimestamp(timestamp).date().isoformat()
            )

    @classmethod
    def __genre(cls, etree):
        elem = etree.find(cls.ITUNES_PREFIX + "category")
        if elem is not None:
            return elem.get("text")
        else:
            return None

    @classmethod
    def __guid(cls, etree):
        return etree.findtext("guid") or get_url(etree.find("enclosure"))

    @classmethod
    def __image(cls, etree):
        elem = etree.find(cls.ITUNES_PREFIX + "image")
        if elem is not None:
            return models.Image(uri=elem.get("href"))
        else:
            return None

    @classmethod
    def __length(cls, etree):
        text = etree.findtext(cls.ITUNES_PREFIX + "duration")
        try:
            groups = cls.DURATION_RE.match(text).groupdict("0")
        except AttributeError:
            return None
        except TypeError:
            return None
        else:
            d = datetime.timedelta(**{k: int(v) for k, v in groups.items()})
            return int(d.total_seconds() * 1000)

    @staticmethod
    def __order(etree):
        text = etree.findtext("pubDate")
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
        "include": lambda e: models.Ref.directory(
            name=e.get("text"), uri=PodcastFeed.getfeeduri(get_url(e))
        ),
        "link": lambda e: models.Ref(
            type=(
                models.Ref.DIRECTORY
                if get_url(e).endswith(".opml")
                else models.Ref.ALBUM
            ),
            name=e.get("text"),
            uri=PodcastFeed.getfeeduri(get_url(e)),
        ),
        "rss": lambda e: models.Ref.album(
            name=e.get("title", e.get("text")),
            uri=PodcastFeed.getfeeduri(e.get("xmlUrl")),
        ),
    }

    def __init__(self, url, root):
        super().__init__(url)
        self.__outlines = root.findall("./body//outline[@type]")

    def items(self, newest_first=None):
        for e in self.__outlines:
            try:
                ref = self.TYPES[e.get("type").lower()]
            except KeyError:
                pass
            else:
                yield ref(e)


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import contextlib
    import json
    import urllib.request
    import sys

    from mopidy.models import ModelJSONEncoder

    parser = argparse.ArgumentParser()
    parser.add_argument("url", metavar="URL")
    parser.add_argument("-i", "--images", action="store_true")
    parser.add_argument("-t", "--tracks", action="store_true")
    args = parser.parse_args()

    with contextlib.closing(urllib.request.urlopen(args.url)) as source:
        feed = parse(source)
    if args.tracks:
        result = list(feed.tracks())
    elif args.images:
        result = dict(feed.images())
    else:
        result = list(feed.items())
    json.dump(result, sys.stdout, cls=ModelJSONEncoder, indent=2)
    sys.stdout.write("\n")
