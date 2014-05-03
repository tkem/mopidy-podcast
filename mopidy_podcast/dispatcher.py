from __future__ import unicode_literals

import logging

import pykka

from .directory import PodcastDirectory
from .models import Ref
from .timers import DebugTimer
from .uritools import urijoin, urisplit, uriunsplit

BASE_URI = 'podcast:'

logger = logging.getLogger(__name__)


def _transform(base, model):
    uri = base.transform(model.uri, strict=True).geturi()
    if not uri.startswith(BASE_URI):
        uri = BASE_URI + uri
    return model.copy(uri=uri)


class PodcastDirectoryActor(pykka.ThreadingActor):

    def __init__(self, directory):
        super(PodcastDirectoryActor, self).__init__()
        self.directory = directory

    def get(self, uri):
        with DebugTimer(logger, 'Getting %s from %s' % (uri, self.directory)):
            return self.directory.get(uri)

    def browse(self, uri, limit=None):
        with DebugTimer(logger, 'Browsing %s in %s' % (uri, self.directory)):
            return self.directory.browse(uri, limit)

    def search(self, uri, terms, attr=None, type=None, limit=None):
        with DebugTimer(logger, 'Searching %s' % self.directory):
            return self.directory.search(uri, terms, attr, type, limit)

    def refresh(self, uri=None):
        with DebugTimer(logger, 'Refreshing %s' % self.directory):
            return self.directory.refresh(uri)

    def on_start(self):
        logger.debug('Starting %s', self.directory)

    def on_stop(self):
        logger.debug('Stopping %s', self.directory)


class PodcastDirectoryDispatcher(PodcastDirectory):

    root_uri = BASE_URI

    root_directories = []

    def __init__(self, directories):
        self.root_directories = []
        self._proxies = {}
        self._schemes = {}

        for d in directories:
            if d.display_name:
                self.root_directories.append(Ref.directory(
                    uri=urijoin(self.root_uri, '//' + d.name + '/'),
                    name=d.display_name
                ))
            proxy = PodcastDirectoryActor.start(d).proxy()
            self._proxies[d.name] = proxy
            self._schemes.update(dict.fromkeys(d.uri_schemes, proxy))

    def get(self, uri):
        proxy, uribase, uriref = self._lookup(uri)
        podcast = proxy.get(uriref).get()
        episodes = tuple(_transform(uribase, e) for e in podcast.episodes)
        return podcast.copy(uri=uri, episodes=episodes)

    def browse(self, uri, limit=None):
        if not uri or uri == self.root_uri:
            return self.root_directories
        proxy, uribase, uriref = self._lookup(uri)
        refs = proxy.browse(uriref, limit).get() or []
        return [_transform(uribase, ref) for ref in refs]

    def search(self, uri, terms, attr=None, type=None, limit=None):
        if not uri or uri == self.root_uri:
            return self._search(terms, attr, type, limit)
        proxy, uribase, uriref = self._lookup(uri)
        refs = proxy.search(uriref, terms, attr, type, limit).get() or []
        return [_transform(uribase, ref) for ref in refs]

    def refresh(self, uri=None, async=False):
        if not uri or uri == self.root_uri:
            futures = [p.refresh() for p in self._proxies.values()]
        else:
            proxy, uribase, uriref = self._lookup(uri)
            futures = [proxy.refresh(uriref)]
        if not async:
            pykka.get_all(futures)

    def stop(self):
        for proxy in self._proxies.values():
            proxy.actor_ref.stop()

    def _lookup(self, uri):
        if uri.startswith(self.root_uri + '//'):
            base = urisplit(uri)
            proxy = self._proxies[base.authority]
            uriref = uriunsplit((None, None) + base[2:])
        elif uri.startswith(self.root_uri):
            base = urisplit(uri[len(self.root_uri):])
            proxy = self._schemes[base.scheme]
            uriref = base.geturi()
        else:
            raise LookupError('Invalid podcast URI: %s' % uri)
        return (proxy, base, uriref)

    def _search(self, terms, attr=None, type=None, limit=None):
        results = []
        for name, proxy in self._proxies.items():
            results.append((name, proxy.search('/', terms, attr, type, limit)))
        # merge results and filter duplicates
        merged = {}
        for name, future in results:
            try:
                refs = future.get() or []
                base = urisplit(urijoin(self.root_uri, '//' + name + '/'))
                result = [_transform(base, ref) for ref in refs]
                merged.update((ref.uri, ref) for ref in result)
            except Exception as e:
                logger.error('Searching podcast directory "%s" failed: %r',
                             base.authority, e)
        return merged.values()[:limit]
