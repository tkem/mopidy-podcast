from __future__ import unicode_literals

from collections import OrderedDict
from threading import RLock
from time import time


class LRUCache(OrderedDict):

    def __init__(self, maxsize, ttl):
        super(LRUCache, self).__init__()
        self._maxsize = maxsize
        self._expires = {}
        self._ttl = ttl
        self._lock = RLock()

    def __getitem__(self, key):
        with self._lock:
            if key in self._expires and self._expires[key] < time():
                del self[key]
            value = super(LRUCache, self).__getitem__(key)
            self._update(key, value)
            return value

    def __setitem__(self, key, value):
        with self._lock:
            if len(self) >= self._maxsize:
                del self[next(iter(self))]
            super(LRUCache, self).__setitem__(key, value)
            self._expires[key] = time() + self._ttl
            self._update(key, value)

    def __delitem__(self, key):
        with self._lock:
            super(LRUCache, self).__delitem__(key)
            del self._expires[key]

    def _update(self, key, value):
        super(LRUCache, self).__delitem__(key)
        super(LRUCache, self).__setitem__(key, value)
