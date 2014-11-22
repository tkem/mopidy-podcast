from __future__ import unicode_literals

import datetime
import email.utils
import logging
import re
import xml.etree.ElementTree

from .models import Podcast, Episode, Image, Enclosure

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


def to_bool(e):
    return e.text.strip().lower() == 'yes' if e.text else None


def to_int(e):
    return int(e.text) if e.text and e.text.isdigit() else None


def to_datetime(e):
    try:
        timestamp = email.utils.mktime_tz(email.utils.parsedate_tz(e.text))
    except AttributeError:
        return None
    except TypeError:
        return None
    return datetime.datetime.utcfromtimestamp(timestamp)


def to_timedelta(e):
    try:
        groups = DURATION_RE.match(e.text).groupdict('0')
    except AttributeError:
        return None
    except TypeError:
        return None
    return datetime.timedelta(**{k: int(v) for k, v in groups.items()})


def to_category(e):
    return e.get('text')


def to_image(e):
    kwargs = {}
    # handle both RSS and itunes images
    kwargs['uri'] = e.get('href', gettag(e, 'url'))
    kwargs['title'] = gettag(e, 'title')
    for name in ('width', 'height'):
        kwargs[name] = gettag(e, name, to_int)
    return Image(**kwargs)


def to_enclosure(e):
    uri = e.get('url')
    type = e.get('type')
    length = int(e.get('length')) if e.get('length', '').isdigit() else None
    return Enclosure(uri=uri, type=type, length=length)


def to_episode(e, feedurl):
    kwargs = {
        'title': gettag(e, 'title'),
        'guid': gettag(e, 'guid'),
        'pubdate': gettag(e, 'pubDate', to_datetime),
        'author': gettag(e, 'itunes:author'),
        'block': gettag(e, 'itunes:block', to_bool),
        'image': gettag(e, 'itunes:image', to_image),
        'duration': gettag(e, 'itunes:duration', to_timedelta),
        'explicit': gettag(e, 'itunes:explicit', to_bool),  # TODO: "clean"
        'order': gettag(e, 'itunes:order', to_int),
        'subtitle': gettag(e, 'itunes:subtitle'),
        'summary': gettag(e, 'itunes:summary'),
        'enclosure': gettag(e, 'enclosure', to_enclosure)

    }
    # FIXME: belongs in library
    if not kwargs['summary']:
        kwargs['summary'] = gettag(e, 'description')
    if not kwargs['guid'] and kwargs['enclosure']:
        kwargs['guid'] = kwargs['enclosure'].uri
    if kwargs['enclosure'] and kwargs['enclosure'].uri:
        kwargs['uri'] = feedurl + '#' + kwargs['enclosure'].uri
    return Episode(**kwargs)


def gettag(etree, tag, convert=None, namespaces=NAMESPACES):
    e = etree.find(tag, namespaces=namespaces)
    if e is None:
        return None
    elif convert:
        return convert(e)
    elif e.text:
        return e.text.strip()
    else:
        return None


def episodekey(model):
    return model.pubdate or datetime.datetime.min


def parse_rss(source):
    uri = source.geturl()
    channel = xml.etree.ElementTree.parse(source).find('channel')
    if channel is None:
        raise TypeError('Not an RSS feed')
    kwargs = {'uri': uri}
    for name in ('title', 'link', 'copyright', 'language'):
        kwargs[name] = gettag(channel, name)
    for name in ('author', 'subtitle', 'summary'):
        kwargs[name] = gettag(channel, 'itunes:' + name)
    for name in ('block', 'complete', 'explicit'):  # TODO: clean
        kwargs[name] = gettag(channel, 'itunes:' + name, to_bool)
    kwargs['pubdate'] = gettag(channel, 'pubDate', to_datetime)
    kwargs['category'] = gettag(channel, 'itunes:category', to_category)
    kwargs['newfeedurl'] = gettag(channel, 'itunes:new-feed-url')
    kwargs['image'] = gettag(channel, 'image', to_image)
    # FIXME: belongs in library?
    if not kwargs['summary']:
        kwargs['summary'] = gettag(channel, 'description')
    if not kwargs['image']:  # TBD: prefer iTunes image over RSS image?
        kwargs['image'] = gettag(channel, 'itunes:image', to_image)

    episodes = []
    for item in channel.iter(tag='item'):
        try:
            episodes.append(to_episode(item, uri))
        except Exception as e:
            logger.warn('Skipping episode for %s: %s', uri, e)
    # TODO: itunes:order, configurable...
    kwargs['episodes'] = sorted(episodes, key=episodekey, reverse=True)

    return Podcast(**kwargs)
