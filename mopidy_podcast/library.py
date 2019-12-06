import itertools
import locale
import logging
import os

import uritools
from mopidy import backend, models

from . import Extension

logger = logging.getLogger(__name__)


def strerror(error):
    if isinstance(error.strerror, bytes):
        return error.strerror.decode(locale.getpreferredencoding())
    else:
        return error.strerror


def get_config_dir(config):
    try:
        return Extension.get_config_dir(config)
    except OSError as e:
        logger.warning(
            "Cannot access %s config directory: %s",
            Extension.dist_name,
            strerror(e),
        )
    except Exception as e:
        logger.warning(
            "Cannot access %s config directory: %s", Extension.dist_name, e
        )
    return None


class PodcastLibraryProvider(backend.LibraryProvider):
    def __init__(self, config, backend):
        super().__init__(backend)
        self.__config_dir = get_config_dir(config)
        self.__browse_root = config[Extension.ext_name]["browse_root"]
        self.__browse_order = config[Extension.ext_name]["browse_order"]
        self.__lookup_order = config[Extension.ext_name]["lookup_order"]
        self.__tracks = {}  # cache tracks for faster lookup

    @property
    def root_directory(self):
        root = self.__browse_root
        if not root:
            return None
        elif root.startswith(("file:", "http:", "https:")):
            uri = uritools.uridefrag("podcast+" + root).uri
            return models.Ref.directory(name="Podcasts", uri=uri)
        elif os.path.isabs(root):
            uri = uritools.uricompose("podcast+file", "", root)
            return models.Ref.directory(name="Podcasts", uri=uri)
        elif self.__config_dir:
            path = os.path.join(self.__config_dir, root)
            uri = uritools.uricompose("podcast+file", "", path)
            return models.Ref.directory(name="Podcasts", uri=uri)
        else:
            logger.error("Cannot retrieve Podcast root directory")
            return None

    def browse(self, uri):
        try:
            feed = self.backend.feeds[uri]
        except Exception as e:
            logger.error("Error retrieving %s: %s", uri, e)  # TODO: raise?
        else:
            return list(feed.items(self.__browse_order == "desc"))
        return []  # FIXME: hide errors from clients

    def get_images(self, uris):
        def key(uri):
            return uritools.uridefrag(uri).uri

        result = {}
        for feeduri, uris in itertools.groupby(sorted(uris, key=key), key=key):
            try:
                images = dict(self.backend.feeds[feeduri].images())
            except Exception as e:
                logger.error("Error retrieving images for %s: %s", feeduri, e)
            else:
                result.update((uri, images.get(uri, [])) for uri in uris)
        return result

    def lookup(self, uri):
        # pop from __tracks since cached tracks shouldn't live too long
        try:
            track = self.__tracks.pop(uri)
        except KeyError:
            logger.debug("Lookup cache miss: %s", uri)
        else:
            return [track]
        try:
            feed = self.backend.feeds[uritools.uridefrag(uri).uri]
        except Exception as e:
            logger.error("Error retrieving %s: %s", uri, e)  # TODO: raise?
        else:
            return self.__lookup(feed, uri)
        return []  # FIXME: hide errors from clients

    def refresh(self, uri=None):
        if uri:
            self.backend.feeds.pop(uritools.uridefrag(uri).uri, None)
        else:
            self.backend.feeds.clear()
        self.__tracks.clear()

    def __lookup(self, feed, uri):
        if uri == feed.uri:
            return list(feed.tracks(self.__lookup_order == "desc"))
        else:
            self.__tracks = tracks = {t.uri: t for t in feed.tracks()}
            try:
                track = tracks.pop(uri)
            except KeyError:
                logger.warning("No such track: %s", uri)  # TODO: raise?
            else:
                return [track]
