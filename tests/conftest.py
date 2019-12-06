import functools
import os
from unittest import mock

import mopidy_podcast as ext
import pytest


@pytest.fixture
def abspath():
    return functools.partial(os.path.join, os.path.dirname(__file__))


@pytest.fixture
def audio():
    return mock.Mock()


@pytest.fixture
def config():
    return {
        "podcast": {
            "browse_root": "Podcasts.opml",
            "browse_order": "desc",
            "lookup_order": "asc",
            "cache_size": 64,
            "cache_ttl": 86400,
            "timeout": 10,
        },
        "core": {"config_dir": os.path.dirname(__file__)},
        "proxy": {},
    }


@pytest.fixture
def backend(config, audio):
    return ext.backend.PodcastBackend(config, audio)


@pytest.fixture
def library(backend):
    return backend.library


@pytest.fixture
def playback(backend):
    return backend.playback
