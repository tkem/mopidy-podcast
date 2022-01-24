import functools
import os
from pathlib import Path
from unittest import mock

import mopidy_podcast as ext
import pytest


@pytest.fixture
def testpath() -> Path:
    return Path(__file__).parent


@pytest.fixture
def abspath(testpath: Path):
    return functools.partial(os.path.join, str(testpath))


@pytest.fixture
def audio():
    return mock.Mock()


@pytest.fixture
def config(testpath: Path):
    return {
        "podcast": {
            "browse_root": "Podcasts.opml",
            "browse_order": "desc",
            "lookup_order": "asc",
            "cache_size": 64,
            "cache_ttl": 86400,
            "timeout": 10,
        },
        "core": {"config_dir": testpath},
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
