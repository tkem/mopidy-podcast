from __future__ import unicode_literals

import collections
import logging
import threading
import time

import pykka

from . import Extension
from .directory import PodcastDirectory
from .models import Ref
from .timers import DebugTimer
from .uritools import urisplit, uriunsplit

logger = logging.getLogger(__name__)


def _transform(base, ref):
    return ref.copy(uri=base.transform(ref.uri, strict=True).geturi())


class PodcastDirectoryActor(pykka.ThreadingActor):

    def __init__(self, directory, config, timeout):
        super(PodcastDirectoryActor, self).__init__()
        self.directory = directory(config, timeout)
        self.root_directory = Ref.directory(
            uri=uriunsplit([None, self.directory.name, '/', None, None]),
            name=self.directory.display_name or self.directory.name
        )

    def get(self, uri):
        with DebugTimer(logger, 'Getting %s from %s' % (uri, self.directory)):
            return self.directory.get(uri)

    def browse(self, uri, limit=None):
        with DebugTimer(logger, 'Browsing %s in %s' % (uri, self.directory)):
            return self.directory.browse(uri, limit)

    def search(self, terms=None, attribute=None, type=None, limit=None):
        with DebugTimer(logger, 'Searching %s' % self.directory):
            return self.directory.search(terms, attribute, type, limit)

    def update(self):
        with DebugTimer(logger, 'Updating %s' % self.directory):
            return self.directory.update()

    def on_stop(self):
        logger.debug('Stopping %r', self.actor_ref)


class PodcastDirectoryController(PodcastDirectory):

    lock = threading.RLock()

    def __init__(self, config, timeout, classes):
        super(PodcastDirectoryController, self).__init__(config, timeout)
        self.cache = self._cache(**config[Extension.ext_name])
        self.names = [cls.name for cls in classes]
        logger.info('Starting %s directories: %s', Extension.dist_name,
                    ', '.join(cls.__name__ for cls in classes))
        self.proxies = {
            cls.name: self._start(cls, config, timeout) for cls in classes
        }

    def get(self, uri):
        if not uri:
            return None
        if uri.startswith('//'):
            base = urisplit(uri)
            proxy = self.proxies[base.authority]
            future = proxy.get(uriunsplit((None, None) + base[2:]))
            return future.get()
        return self.get_cached(uri, super(PodcastDirectoryController, self))

    def browse(self, uri, limit=None):
        if not uri:
            return self.root_directories
        if uri.startswith('//'):
            base = urisplit(uri)
            proxy = self.proxies[base.authority]
            future = proxy.browse(uriunsplit((None, None) + base[2:]), limit)
            return [_transform(base, ref) for ref in future.get()]
        return super(PodcastDirectoryController, self).browse(uri, limit)

    def search(self, terms=None, attribute=None, type=None, limit=None):
        proxies = [self.proxies[name] for name in self.names]
        futures = [p.search(terms, attribute, type, limit) for p in proxies]
        results = zip(self.names, futures)
        # merge results and filter duplicates, but keep order
        result = collections.OrderedDict()
        for name, future in results:
            try:
                refs = future.get()
            except Exception as e:
                logger.error('Searching directory %s failed: %r', name, e)
                continue
            if not refs:
                continue
            base = urisplit('//' + name)
            for ref in refs:
                if limit and len(result) >= limit:
                    break
                result[ref.uri] = _transform(base, ref)
        return result.values()

    def update(self, async=False):
        with self.lock:
            self.cache.clear()
        with DebugTimer(logger, 'Updating podcast directories'):
            futures = [p.update() for p in self.proxies.values()]
            return None if async else pykka.get_all(futures)

    def stop(self):
        logger.info('Stopping %s directories', Extension.dist_name)
        for proxy in self.proxies.values():
            proxy.actor_ref.stop()
        logger.debug('Stoppped all %s directories', Extension.dist_name)

    def get_cached(self, uri, directory):
        if uri.startswith('/'):
            key = '//' + directory.name + uri
        else:
            key = uri
        with self.lock:
            try:
                return self.cache[key]
            except KeyError:
                pass
        with DebugTimer(logger, 'Getting podcast %s' % uri):
            podcast = directory.get(uri)
        with self.lock:
            self.cache[key] = podcast
        return podcast

    @property
    def root_directories(self):
        futures = [d.root_directory for d in self.proxies.values()]
        return [ref for ref in pykka.get_all(futures) if ref]

    def _cache(self, cache_size=0, cache_ttl=0, **kwargs):
        # TODO: integrate with cachetools
        from .cachetools import LRUCache

        expires = {}

        class Cache(LRUCache):

            def __getitem__(self, key):
                if expires[key] < time.time():
                    del self[key]
                return super(Cache, self).__getitem__(key)

            def __setitem__(self, key, value):
                if len(self) >= self.maxsize:
                    now = time.time()
                    for key in self.keys():
                        if expires[key] < now:
                            del self[key]
                super(Cache, self).__setitem__(key, value)
                expires[key] = time.time() + cache_ttl

            def __delitem__(self, key):
                super(Cache, self).__delitem__(key)
                del expires[key]

        return Cache(cache_size)

    def _start(self, cls, config, timeout):
        controller = self

        class CachedDirectory(cls):

            def get(self, uri):
                directory = super(CachedDirectory, self)
                return controller.get_cached(uri, directory)

            def __str__(self):
                return '%s<%s>(%s)' % (
                    self.__class__.__name__,
                    cls.__name__,
                    self.name
                )

        actor = PodcastDirectoryActor.start(CachedDirectory, config, timeout)
        logger.debug('%r started', actor)
        return actor.proxy()
