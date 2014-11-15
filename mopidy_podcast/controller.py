from __future__ import unicode_literals

import logging
import pykka
import uritools

from .models import Ref

logger = logging.getLogger(__name__)


def transform(base, model):
    ref = base.transform(model.uri, strict=True)
    if ref.scheme != base.scheme:
        return model.copy(uri='podcast+' + ref.geturi())
    else:
        return model.copy(uri=ref.geturi())


class PodcastDirectoryActor(pykka.ThreadingActor):

    def __init__(self, directory):
        super(PodcastDirectoryActor, self).__init__()
        self.directory = directory

    def get(self, uri):
        return self.directory.get(uri)

    def browse(self, uri, limit=None):
        return self.directory.browse(uri, limit)

    def search(self, uri, terms, attr=None, type=None, limit=None):
        return self.directory.search(uri, terms, attr, type, limit)

    def refresh(self, uri=None):
        return self.directory.refresh(uri)

    def on_start(self):
        logger.debug('Starting %s', self.directory)

    def on_stop(self):
        logger.debug('Stopping %s', self.directory)


class PodcastDirectoryController(object):

    root_uri = 'podcast:'

    def __init__(self, directories):
        self.root_directories = []
        self._base_uris = {}
        self._proxies = {}
        self._schemes = {}

        for d in directories:
            uri = 'podcast://%s/' % d.name
            if d.root_name:
                name = d.root_name
                self.root_directories.append(Ref.directory(uri=uri, name=name))
            self._base_uris[d.name] = uritools.urisplit(uri)
            proxy = PodcastDirectoryActor.start(d).proxy()
            self._proxies[d.name] = proxy
            self._schemes.update(dict.fromkeys(d.uri_schemes, proxy))

    def get(self, uri):
        uribase, uriref, proxy = self._lookup(uri)
        podcast = proxy.get(uriref).get()
        # FIXME: episode w/o uri shouldn't be possible...
        episodes = (transform(uribase, e) for e in podcast.episodes if e.uri)
        return podcast.copy(uri=uri, episodes=episodes)

    def browse(self, uri, limit=None):
        if uri and uri != self.root_uri:
            uribase, uriref, proxy = self._lookup(uri)
            refs = proxy.browse(uriref, limit).get() or []
            return [transform(uribase, ref) for ref in refs]
        else:
            return self.root_directories

    def search(self, uri, terms, attr=None, type=None, limit=None):
        if uri and uri != self.root_uri:
            uribase, uriref, proxy = self._lookup(uri)
            refs = proxy.search(uriref, terms, attr, type, limit).get() or []
            return [transform(uribase, ref) for ref in refs]
        else:
            return self._search(terms, attr, type, limit)

    def refresh(self, uri=None, async=False):
        if uri and uri != self.root_uri:
            _, uriref, proxy = self._lookup(uri)
            futures = [proxy.refresh(uriref)]
        else:
            futures = [p.refresh() for p in self._proxies.values()]
        if not async:
            pykka.get_all(futures)

    def stop(self):
        for proxy in self._proxies.values():
            proxy.actor_ref.stop()

    def _lookup(self, uri):
        parts = uritools.urisplit(uri)
        if parts.scheme == 'podcast':
            ref = uritools.uriunsplit((None, None) + parts[2:])
            proxy = self._proxies[parts.authority]
        else:
            scheme = parts.scheme.partition('+')[2]
            ref = uritools.uriunsplit((scheme,) + parts[1:])
            proxy = self._schemes[scheme]
        return (parts, ref, proxy)

    def _search(self, terms, attr=None, type=None, limit=None):
        results = []
        for name, proxy in self._proxies.items():
            results.append((name, proxy.search('/', terms, attr, type, limit)))
        # merge results, filter duplicates by uri
        merged = {}
        for name, future in results:
            try:
                refs = future.get() or []
                base = self._base_uris[name]
                results = [transform(base, ref) for ref in refs]
                merged.update((ref.uri, ref) for ref in results)
            except Exception as e:
                logger.error('Searching "%s" failed: %s', name, e)
        return merged.values()[:limit]  # arbitrary selection
