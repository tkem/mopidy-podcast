Mopidy-Podcast
========================================================================

Mopidy-Podcast is a Mopidy_ extension for browsing and playing
podcasts.

This extension lets you browse podcasts distributed as RSS feeds and
play individual episodes in a variety of audio formats.  Podcasts are
mapped to albums, while podcast episodes are shown as tracks in
Mopidy, with metadata converted to Mopidy’s native data model where
applicable.  OPML 2.0 subscription lists and directories are also
supported for multi-level browsing.

For more information, please see Mopidy-Podcast's online
documentation_.


Installation
------------------------------------------------------------------------

On Debian Linux and Debian-based distributions like Ubuntu or
Raspbian, install the ``mopidy-podcast`` package from
apt.mopidy.com_::

  apt-get install mopidy-podcast

Otherwise, install the Python package from PyPI_::

  pip install Mopidy-Podcast


Configuration
------------------------------------------------------------------------

Please refer to the documentation's `Configuration`_ section for a
discussion of the available configuration values.


Project Resources
------------------------------------------------------------------------

.. image:: http://img.shields.io/pypi/v/Mopidy-Podcast.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Podcast/
    :alt: Latest PyPI version

.. image:: http://img.shields.io/pypi/dm/Mopidy-Podcast.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Podcast/
    :alt: Number of PyPI downloads

.. image:: http://img.shields.io/travis/tkem/mopidy-podcast/master.svg?style=flat
    :target: https://travis-ci.org/tkem/mopidy-podcast/
    :alt: Travis CI build status

.. image:: http://img.shields.io/coveralls/tkem/mopidy-podcast/master.svg?style=flat
   :target: https://coveralls.io/r/tkem/mopidy-podcast/
   :alt: Test coverage

.. image:: https://readthedocs.org/projects/mopidy-podcast/badge/?version=latest&style=flat
   :target: http://mopidy-podcast.readthedocs.org/en/latest/
   :alt: Documentation Status

- `Issue Tracker`_
- `Source Code`_
- `Change Log`_


License
------------------------------------------------------------------------

Copyright (c) 2014-2016 Thomas Kemmer.

Licensed under the `Apache License, Version 2.0`_.


.. _Mopidy: http://www.mopidy.com/
.. _apt.mopidy.com: http://apt.mopidy.com/

.. _PyPI: https://pypi.python.org/pypi/Mopidy-Podcast/
.. _Documentation: http://mopidy-podcast.readthedocs.org/en/latest/
.. _Configuration: http://mopidy-podcast.readthedocs.org/en/latest/config.html
.. _Issue Tracker: https://github.com/tkem/mopidy-podcast/issues/
.. _Source Code: https://github.com/tkem/mopidy-podcast
.. _Change Log: https://github.com/tkem/mopidy-podcast/blob/master/CHANGES.rst

.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
