from __future__ import unicode_literals

import logging
import pykka

from collections import OrderedDict

from . import Extension, PodcastDirectory
from .models import Ref
from .uritools import urisplit, uridefrag, uricompose, urijoin

logger = logging.getLogger(__name__)


class PodcastDirectoryController(PodcastDirectory):

    class Actor(pykka.ThreadingActor):

        pykka_traversable = True

        root_directory = None

        def __init__(self, cls, *args, **kwargs):
            super(PodcastDirectoryController.Actor, self).__init__()
            self.cls = cls
            self.args = args
            self.kwargs = kwargs

        def on_start(self):
            self.directory = self.cls(*self.args, **self.kwargs)
            if self.directory.display_name:
                self.root_directory = Ref.directory(
                    uri=uricompose('podcast', self.cls.name, '/'),
                    name=self.directory.display_name
                )

        def on_stop(self):
            self.directory = None

        def get(self, uri, cached=True):
            return self.directory.get(uri, cached)

        def browse(self, uri):
            return self.directory.browse(uri)

        def search(self, terms=None, attribute=None, limit=None):
            return self.directory.search(terms, attribute, limit)

        def refresh(self, uri=None):
            return self.directory.refresh(uri)

    def __init__(self, backend, classes):
        super(PodcastDirectoryController, self).__init__(backend)
        logger.info('Starting %s directories: %s', Extension.dist_name,
                    ', '.join(cls.__name__ for cls in classes))
        self.ordered = [cls.name for cls in classes]  # for search
        self.proxies = {cls.name: self._proxy(cls) for cls in classes}

    def get(self, uri, cached=True):
        split = urisplit(uri)
        if not split.authority:
            return self._get(split.getpath(), cached)
        elif split.authority in self.proxies:
            return self.proxies[split.authority].get(split.path, cached).get()
        else:
            logger.warn('Podcast directory %s not found', split.authority)
            return None

    def browse(self, uri):
        if not uri:
            futures = [d.root_directory for d in self.proxies.values()]
            return [ref for ref in pykka.get_all(futures) if ref]
        split = urisplit(uri)
        if not split.authority:
            refs = self._browse(split.getpath())
        elif split.authority in self.proxies:
            refs = self.proxies[split.authority].browse(split.path).get()
        else:
            logger.warn('Podcast directory %s not found', split.authority)
            refs = []
        return [self._wrap(ref, uri) for ref in refs]

    def search(self, terms=None, attribute=None, limit=None):
        proxies = [self.proxies[name] for name in self.ordered]
        futures = [p.search(terms, attribute, limit) for p in proxies]
        results = zip(self.ordered, pykka.get_all(futures))  # [(name, result)]

        # wrap refs, filter duplicates
        result = OrderedDict()
        for name, refs in results:
            base = uricompose('podcast', name, '/')
            refs = [self._wrap(ref, base) for ref in refs]
            result.update((ref.uri, ref) for ref in refs)
        return result.values()[:limit]

    def refresh(self, uri=None, async=False):
        futures = [p.refresh(uri) for p in self.proxies.values()]
        return pykka.get_all(futures) if async else None

    def stop(self):
        logger.info('Stopping %s directories', Extension.dist_name)
        for proxy in self.proxies.values():
            proxy.actor_ref.stop()
        logger.debug('Stoppped all %s directories', Extension.dist_name)

    def _proxy(self, cls):
        return self.Actor.start(cls, self.backend).proxy()

    def _get(self, url, cached):
        return super(PodcastDirectoryController, self).get(url, cached)

    def _browse(self, url):
        refs = []
        podcast = super(PodcastDirectoryController, self).get(url)
        for e in podcast.episodes[:self.backend.max_episodes]:
            if not e.enclosure or not e.enclosure.url:
                logger.debug('Skipping podcast episode w/o enclosure: %r', e)
                continue
            ref = Ref.episode(uri=url + '#' + e.enclosure.url, name=e.title)
            refs.append(ref)
        return refs

    def _wrap(self, ref, base=None):
        uri = urijoin(base or '', ref.uri, strict=True)
        if not uri.startswith('podcast:'):
            d = uridefrag(uri)
            if d.fragment:
                uri = uricompose('podcast', path=d.base) + '#' + d.fragment
            else:
                uri = uricompose('podcast', path=d.base)
        #logger.info('WRAP: %r %r -> %r', ref, base, uri)
        return ref.copy(uri=uri)
