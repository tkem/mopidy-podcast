from __future__ import unicode_literals

import datetime
import logging
import re

# import xml.etree.ElementTree as ET

#ET.register_namespace('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')

#print ET._namespace_map

#from mopidy.models import Album, Artist, Track, Ref

#from .uritools import uricompose

DURATION_RE = re.compile(r"""
(?:
    (?:(?P<hours>\d+):)?
    (?P<minutes>\d+):
)?
(?P<seconds>\d+)
""", flags=re.VERBOSE)

XMLNS = dict(itunes='http://www.itunes.com/dtds/podcast-1.0.dtd')

logger = logging.getLogger(__name__)


def _settagattr(obj, elem, tag, attr=None, convert=None, default=None):
    if ':' in tag:
        e = elem.find(tag, namespaces=XMLNS)
    else:
        e = elem.find(tag)

    if e is None:
        setattr(obj, attr or tag, default)
    elif convert:
        setattr(obj, attr or tag, convert(e.text))  # FIXME: convert(e)
    else:
        setattr(obj, attr or tag, e.text)


def _parse_datetime(s):
    from email.utils import mktime_tz, parsedate_tz
    try:
        return datetime.datetime.fromtimestamp(mktime_tz(parsedate_tz(s)))
    except AttributeError:
        return None
    except TypeError:
        return None


def _parse_timedelta(s):
    try:
        groups = DURATION_RE.match(s or '').groupdict('0')
        return datetime.timedelta(**{k: int(v) for k, v in groups.items()})
    except AttributeError:
        return None
    except TypeError:
        return None


class Podcast(object):
    """
    Podcast implementation according to
    https://www.apple.com/itunes/podcasts/specs.html
    """

    # fallbacks
    title = None
    link = None
    #description = None
    language = None
    copyright = None
    author = None
    block = None
    category = None  # FIXME: multiple, sub-categories
    image = {}  # FIXME: attributes from either image?
    explicit = None
    complete = None
    #new_feed_url = None
    owner = {}  # TODO (frozent default dict?)
    subtitle = None
    summary = None
    #keywords = frozenset()

    def __init__(self, url):
        self.url = url
        self.update()

    def update(self, url=None):
        from urllib2 import urlopen
        from xml.etree.ElementTree import fromstring

        root = fromstring(urlopen(self.url or url).read())
        channel = root.find('channel')

        for i in ('title', 'link', 'description'):
            setattr(self, i, channel.findtext(i))

        self.language = channel.findtext('language')
        self.copyright = channel.findtext('copyright')
        self.subtitle = channel.findtext('itunes:subtitle', namespaces=XMLNS)
        #self.author = channel.findtext('{%s}author' % XMLNS['itunes'])
        self.author = channel.findtext('itunes:author', namespaces=XMLNS)
        self.summary = channel.findtext('itunes:summary', namespaces=XMLNS)
        #self.author = channel.findtext('itunes:author', namespaces=XMLNS)
        # self.owner
        self.image = channel.find('itunes:image', namespaces=XMLNS).get('href')
        """
        <image>
          <url>http://www.w3schools.com/images/logo.gif</url>
          <title>W3Schools.com</title>
          <link>http://www.w3schools.com</link>
        </image>
        """
        category = channel.find('itunes:category', namespaces=XMLNS)
        if category is not None:
            self.category = category.get('text')
        # self.subcategories

        self.episodes = []
        for i in channel.iter(tag='item'):
            self.episodes.append(self.Episode(i))

    class Episode(object):

        title = None
        link = None
        description = None
        #pub_date = None
        enclosure = None
        guid = None

        author = None
        block = None
        image = None
        duration = None
        explicit = None
        #is_closed_captioned = None
        order = None
        subtitle = None
        summary = None

        def __init__(self, item):
            for tag in ('title', 'link', 'description', 'guid'):
                _settagattr(self, item, tag)
            _settagattr(self, item, 'pubDate', 'pubdate', convert=_parse_datetime)
            self.enclosure = item.find('enclosure').attrib  # FIXME: not present?

            for tag in ('author', 'block', 'explicit', 'subtitle', 'summary'):
                _settagattr(self, item, 'itunes:' + tag, tag)
            self.duration = _parse_timedelta(
                item.findtext('itunes:duration', namespaces=XMLNS))
            self.order = item.findtext('itunes:order', namespaces=XMLNS)  # FIXME: int
            # TODO: image w/fallback (normalize url/href)
            # TODO: enclosure.url as guid if not set

        def __cmp__(self, other):
            # TODO: order
            if self.pubdate and other.pubdate:
                return cmp(self.pubdate, other.pubdate)
            elif self.pubdate:
                return -1
            else:
                return 0  # FIXME

        __hash__ = None


if __name__ == '__main__':
    import argparse

    logging.basicConfig()

    parser = argparse.ArgumentParser()
    parser.add_argument('url', metavar='URL')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    pc = Podcast(args.url)
    print "%s [%s]" % (pc.title, pc.author)
    print pc.image
    print pc.language
    print pc.link
    print pc.copyright
    print pc.subtitle
    print pc.summary
    print pc.description
    print pc.category
    #print "owner: %s" % pc.owner

    for e in sorted(pc.episodes):
        print "%s: %s / %s [%s]" % (e.pubdate, e.title, e.subtitle, e.duration)
        if args.verbose:
            print "  %r" % e.enclosure
            print "  link: %s" % e.link
            print "  guid: %s" % e.guid
            print "  order: %s" % e.order
            print "  %s" % e.summary  # HTML?
