from __future__ import unicode_literals

import logging

from collections import namedtuple

from . import PodcastDirectory
from .models import Ref
from .utils import DebugTimer

logger = logging.getLogger(__name__)


class FeedsDirectory(PodcastDirectory):

    IndexEntry = namedtuple('IndexEntry', 'ref attributes')

    name = 'feeds'

    def __init__(self, backend):
        super(FeedsDirectory, self).__init__(backend)
        self.display_name = self.config['feeds_label']
        self.index = {}
        self.refresh()

    @property
    def config(self):
        return self.backend.config['podcast']

    def browse(self, uri):
        if not uri or uri == '/':
            return [e.ref for e in self._podcasts()]
        else:
            return super(FeedsDirectory, self).browse(uri)

    def search(self, terms=None, attribute=None, limit=None):
        if not terms:
            return [e.ref for e in self.index.values()][:limit]
        refs = []
        with DebugTimer(logger, 'Searching feeds index'):
            terms = [term.lower() for term in terms]
            for e in self.index.values():
                if limit and len(refs) >= limit:
                    break
                if all(term in e.attributes[attribute] for term in terms):
                    refs.append(e.ref)
        return refs

    def refresh(self, uri=None):
        index = self.index.copy()
        with DebugTimer(logger, 'Updating feeds index'):
            for url in self.config['feeds']:
                try:
                    podcast = self.get(url, False)  # no cache
                except Exception as e:
                    logger.error('Error loading podcast %s: %r', url, e)
                    continue  # keep existing entry, if any
                entry = self._index_podcast(podcast, url)
                for episode in podcast.episodes:
                    if not episode.enclosure or not episode.enclosure.url:
                        continue
                    e = self._index_episode(episode, url, entry.attributes)
                    index[e.ref.uri] = e
                index[url] = entry
        self.index = index

    def _podcasts(self):
        return [e for e in self.index.values() if e.ref.type == Ref.PODCAST]

    def _episodes(self):
        return [e for e in self.index.values() if e.ref.type == Ref.EPISODE]

    def _index_podcast(self, p, url):
        ref = Ref.podcast(uri=url, name=p.title)
        attributes = {
            self.AUTHOR: (p.author or '').lower(),
            self.CATEGORY: (p.category or '').lower(),
            self.DESCRIPTION: (p.description or '').lower(),
            self.KEYWORDS: ','.join(p.keywords).lower(),
            self.TITLE: (p.title or '').lower(),
        }
        attributes[None] = '\n'.join(attributes.values())
        return self.IndexEntry(ref, attributes)

    def _index_episode(self, e, url, defaults):
        ref = Ref.episode(uri=url + '#' + e.enclosure.url, name=e.title)
        attributes = defaults.copy()
        if e.title:
            attributes[self.TITLE] = e.title.lower()
        if e.author:
            attributes[self.AUTHOR] = e.author.lower()
        if e.description:
            attributes[self.DESCRIPTION] = e.description.lower()
        if e.keywords:
            attributes[self.KEYWORDS] = '\t'.join(e.keywords).lower()
        attributes[None] = '\n'.join(attributes.values())
        return self.IndexEntry(ref, attributes)
