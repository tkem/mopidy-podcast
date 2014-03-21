from __future__ import unicode_literals

import collections
import datetime
import itertools
import logging

from . import Extension
from .directory import PodcastDirectory
from .models import Ref

logger = logging.getLogger(__name__)


def _by_pubdate(e):
    return e.pubdate if e.pubdate else datetime.datetime.min


class FeedsDirectory(PodcastDirectory):

    Entry = collections.namedtuple('Entry', 'ref index pubdate')

    name = 'feeds'

    def __init__(self, config, timeout):
        super(FeedsDirectory, self).__init__(config, timeout)
        self.display_name = config[Extension.ext_name]['feeds_label']
        self._feeds = config[Extension.ext_name]['feeds']
        self._podcasts = []
        self._episodes = []

    def browse(self, uri, limit=None):
        if not uri or uri == '/':
            return [e.ref for e in self._podcasts]
        else:
            return super(FeedsDirectory, self).browse(uri, limit)

    def search(self, terms=None, attribute=None, type=None, limit=None):
        if type == Ref.PODCAST:
            entries = iter(self._podcasts)
        elif type == Ref.EPISODE:
            entries = iter(self._episodes)
        else:
            entries = itertools.chain(self._podcasts, self._episodes)
        if not terms:
            return [e.ref for e in entries][:limit]
        terms = [term.lower() for term in terms]
        refs = []
        for e in entries:
            if limit and len(refs) >= limit:
                break
            if all(term in e.index.get(attribute, '') for term in terms):
                refs.append(e.ref)
        return refs

    def update(self):
        podcasts = []
        episodes = []
        for feedurl in self._feeds:
            try:
                podcast = self.get(feedurl)
            except Exception as e:
                logger.error('Error loading podcast %s: %r', feedurl, e)
                continue  # TODO: keep existing entry?
            e = self._index_podcast(podcast, feedurl)
            for episode in podcast.episodes:
                episodes.append(self._index_episode(episode, feedurl, e.index))
            podcasts.append(e)
        podcasts.sort(key=_by_pubdate, reverse=True)
        episodes.sort(key=_by_pubdate, reverse=True)
        self._podcasts = podcasts
        self._episodes = episodes

    def _index_podcast(self, podcast, feedurl):
        ref = Ref.podcast(uri=feedurl, name=podcast.title)
        index = {
            PodcastDirectory.TITLE: (podcast.title or '').lower(),
            PodcastDirectory.AUTHOR: (podcast.author or '').lower(),
            PodcastDirectory.CATEGORY: (podcast.category or '').lower(),
            PodcastDirectory.DESCRIPTION: (podcast.description or '').lower(),
            PodcastDirectory.KEYWORDS: ','.join(podcast.keywords).lower()
        }
        index[None] = '\n'.join(index.values())
        return self.Entry(ref, index, podcast.pubdate)

    def _index_episode(self, episode, feedurl, defaults):
        uri = feedurl + '#' + episode.enclosure.url
        ref = Ref.episode(uri=uri, name=episode.title)
        index = defaults.copy()
        if episode.title:
            index[PodcastDirectory.TITLE] = episode.title.lower()
        if episode.author:
            index[PodcastDirectory.AUTHOR] = episode.author.lower()
        if episode.description:
            index[PodcastDirectory.DESCRIPTION] = episode.description.lower()
        if episode.keywords:
            index[PodcastDirectory.KEYWORDS] = ','.join(episode.keywords).lower()
        index[None] = '\n'.join(index.values())
        return self.Entry(ref, index, episode.pubdate)
