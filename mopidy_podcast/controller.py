from __future__ import unicode_literals

import logging
import pykka

from .models import Ref
from .timers import DebugTimer
from .uritools import urisplit, uriunsplit

BASE_URI = 'podcast:'

logger = logging.getLogger(__name__)


def _root_uri(name):
    return BASE_URI + '//' + name + '/'


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


class PodcastDirectoryController(object):

    root_uri = BASE_URI

    def __init__(self, directories):
        self.root_directories = []
        self._proxies = {}
        self._schemes = {}

        for d in directories:
            if d.root_name:
                root = Ref.directory(uri=_root_uri(d.name), name=d.root_name)
                self.root_directories.append(root)
            proxy = PodcastDirectoryActor.start(d).proxy()
            self._proxies[d.name] = proxy
            self._schemes.update(dict.fromkeys(d.uri_schemes, proxy))

    def get(self, uri):
        uribase, uriref, proxy = self._lookup(uri)
        podcast = proxy.get(uriref).get()
        episodes = (_transform(uribase, e) for e in podcast.episodes if e.uri)
        return podcast.copy(uri=uri, episodes=episodes)

    def browse(self, uri, limit=None):
        if not uri or uri == self.root_uri:
            return self.root_directories
        uribase, uriref, proxy = self._lookup(uri)
        refs = proxy.browse(uriref, limit).get() or []
        return [_transform(uribase, ref) for ref in refs]

    def search(self, uri, terms, attr=None, type=None, limit=None):
        if not uri or uri == self.root_uri:
            return self._search(terms, attr, type, limit)
        uribase, uriref, proxy = self._lookup(uri)
        refs = proxy.search(uriref, terms, attr, type, limit).get() or []
        return [_transform(uribase, ref) for ref in refs]

    def refresh(self, uri=None, async=False):
        if not uri or uri == self.root_uri:
            futures = [p.refresh() for p in self._proxies.values()]
        else:
            uribase, uriref, proxy = self._lookup(uri)
            futures = [proxy.refresh(uriref)]
        if not async:
            pykka.get_all(futures)

    def stop(self):
        for proxy in self._proxies.values():
            proxy.actor_ref.stop()

    def _lookup(self, uri):
        if uri.startswith(self.root_uri + '//'):
            uribase = urisplit(uri)
            uriref = uriunsplit((None, None) + uribase[2:])
            proxy = self._proxies[uribase.authority]
        elif uri.startswith(self.root_uri):
            uribase = urisplit(uri[len(self.root_uri):])
            uriref = uribase.geturi()
            proxy = self._schemes[uribase.scheme]
        else:
            raise LookupError('Invalid podcast URI: %s' % uri)
        return (uribase, uriref, proxy)

    def _search(self, terms, attr=None, type=None, limit=None):
        results = []
        for name, proxy in self._proxies.items():
            results.append((name, proxy.search('/', terms, attr, type, limit)))
        # merge results, filter duplicates by uri
        merged = {}
        for name, future in results:
            try:
                refs = future.get() or []
                base = urisplit(_root_uri(name))
                results = [_transform(base, ref) for ref in refs]
                merged.update((ref.uri, ref) for ref in results)
            except Exception as e:
                logger.error('Searching "%s" failed: %s', name, e)
        return merged.values()[:limit]  # arbitrary selection
